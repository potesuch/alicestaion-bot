import os
import tempfile
import pickle
from pydub import AudioSegment
from aiohttp import ClientSession
from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.formatting import as_list
from aiogram.fsm.context import FSMContext

from ..aioquasar_api import YandexQuasar
from ..speech_to_text import stp

from ..states import BaseStates
from ..keyboards.for_authorized import get_authorized_kb

router = Router()

@router.message(BaseStates.in_conv, F.text.lower()=='выход')
async def conversation_exit(message: Message, state: FSMContext):
    async with ClientSession() as session:
        data = await state.get_data()
        cookies = pickle.loads(eval(data.get('cookies')))
        session.cookie_jar._cookies = cookies
        ya_quasar = YandexQuasar(session)
        await ya_quasar.get()
        scenarios = ya_quasar.scenarios
        speakers = ya_quasar.speakers
        speaker_list = []
        for i, speaker in enumerate(speakers):
            speaker_list.append(f'{i+1}. {speaker["name"]}')
        content = as_list('Выберите станцию:', *speaker_list)
        await state.set_state(BaseStates.authorized)
        await state.update_data(scenarios=scenarios,
                                speakers=speakers)
        await message.answer(**content.as_kwargs(),
                             reply_markup=get_authorized_kb(len(speaker_list)))


@router.message(BaseStates.in_conv, F.text)
async def conversation_message(message: Message, state: FSMContext):
    async with ClientSession() as session:
        data = await state.get_data()
        cookies = pickle.loads(eval(data.get('cookies')))
        scenario_id = data.get('scenario_id')
        session.cookie_jar._cookies = cookies
        ya_quasar = YandexQuasar(session)
        command = message.text
        await ya_quasar.update_scenario(scenario_id, command)
        await ya_quasar.exec_scenario(scenario_id)
        await message.answer('Выполнено')


@router.message(BaseStates.in_conv, F.voice)
async def conversation_voice(message: Message, state: FSMContext):
        with tempfile.TemporaryDirectory() as tempdir:
            voice_path = os.path.join(tempdir, f'{message.voice.file_id}.mp3')
            voice = await message.bot.download(message.voice)
            voice_mp3 = AudioSegment.from_ogg(voice)
            voice_mp3.export(voice_path, format='mp3')
            command = await stp.transcribe(voice_path)
        if command:
            async with ClientSession() as session:
                data = await state.get_data()
                cookies = pickle.loads(eval(data.get('cookies')))
                scenario_id = data.get('scenario_id')
                session.cookie_jar._cookies = cookies
                ya_quasar = YandexQuasar(session)
                await ya_quasar.update_scenario(scenario_id, command)
                await ya_quasar.exec_scenario(scenario_id)
                await message.answer('Выполнено')
        else:
            await message.answer('Голосовое не распознано')
