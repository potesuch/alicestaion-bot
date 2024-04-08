import pickle
from aiohttp import ClientSession
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from aioquasar_api import YandexQuasar
from states import BaseStates
from keyboards.for_conversation import get_conversation_kb

router = Router()


@router.message(BaseStates.authorized, F.text.lower()=='выйти из аккаунта')
async def logout(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Вы вышли из аккаунта, чтобы снова авторизоваться '
                         'нажмите /start')


@router.message(BaseStates.authorized, F.text)
async def select_station(message: Message, state: FSMContext):
    async with ClientSession() as session:
        data = await state.get_data()
        cookies = pickle.loads(eval(data.get('cookies')))
        scenarios = data.get('scenarios')
        speakers = data.get('speakers')
        session.cookie_jar._cookies = cookies
        ya_quasar = YandexQuasar(session)
        if message.text.isnumeric() and int(message.text)-1 in range(len(speakers)):
            speaker_id = speakers[int(message.text)-1]['id']
            scenario_names = (scenario['name'] for scenario in scenarios)
            if f'bot_command_{speaker_id}' not in scenario_names:
                await ya_quasar.create_scenario(speaker_id)
            await ya_quasar.get_scenarios()
            scenarios = ya_quasar.scenarios
            for scenario in scenarios:
                if scenario['name'] == f'bot_command_{speaker_id}':
                    scenario_id = scenario['id']
                    break
            await state.set_state(BaseStates.in_conv)
            await state.update_data(speaker_id=speaker_id,
                                    scenario_id=scenario_id)
            await message.answer('Введите или скажите команду. Нажмите "выход", '
                                 'чтобы сменить станцию:',
                                 reply_markup=get_conversation_kb())
        else:
            await message.answer('Неверный номер устройства')
