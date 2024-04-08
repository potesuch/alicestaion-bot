import pickle
from aiohttp import ClientSession
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list

from ..aioquasar_api import YandexSession
from ..aioquasar_api import YandexQuasar  # Сделать в одну строку

from ..states import BaseStates
from ..keyboards.for_authorized import get_authorized_kb

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(BaseStates.unauthorized)
    await message.answer('Введите логин и пароль в формате "login:password":')


@router.message(BaseStates.unauthorized, F.text)
async def login_password(message: Message, state: FSMContext):
    if ':' in message.text:
        async with ClientSession() as session:
            login, password = message.text.split(':')
            ya_session = YandexSession(session, login, password)
            auth_payload, auth_state = await ya_session.login()
            cookies = str(pickle.dumps(session.cookie_jar._cookies))
            if auth_state == 'wrong_login':
                await message.answer('Аккаунт не существует')
            elif auth_state == 'wrong_password':
                await message.answer('Неверный пароль')
            elif auth_state == 'auth_challenge':
                await state.set_state(BaseStates.code_verification)
                await state.update_data(cookies=cookies,
                                        auth_payload=auth_payload)
                await message.answer('Введите код поддверждения:')
            else:
                ya_quasar = YandexQuasar(session)
                await ya_quasar.get()
                scenarios = ya_quasar.scenarios
                speakers = ya_quasar.speakers
                speaker_list = []
                for i, speaker in enumerate(speakers):
                    speaker_list.append(f'{i+1}. {speaker["name"]}')
                content = as_list('Выберите станцию:', *speaker_list)
                await state.set_state(BaseStates.authorized)
                await state.update_data(cookies=cookies, scenarios=scenarios,
                                        speakers=speakers)
                await message.answer(**content.as_kwargs(),
                                     reply_markup=get_authorized_kb(len(speaker_list)))
    else:
        await message.answer('Неверный формат данных')


@router.message(BaseStates.code_verification, F.text)
async def code_auth(message: Message, state: FSMContext):
    code = message.text
    if code.isnumeric():
        async with ClientSession() as session:
            data = await state.get_data()
            cookies = pickle.loads(eval(data.get('cookies')))
            auth_payload = data.get('auth_payload')
            session.cookie_jar._cookies = cookies
            ya_session = YandexSession(session)
            status = await ya_session.code_auth(auth_payload, code)
            if status == 'ok':
                cookies = str(pickle.dumps(session.cookie_jar._cookies))
                ya_quasar = YandexQuasar(session)
                await ya_quasar.get()
                scenarios = ya_quasar.scenarios
                speakers = ya_quasar.speakers
                speaker_list = []
                for i, speaker in enumerate(speakers):
                    speaker_list.append(f'{i+1}. {speaker["name"]}')
                content = as_list('Выберите станцию:', *speaker_list)
                await state.set_state(BaseStates.authorized)
                await state.update_data(cookies=cookies, scenarios=scenarios,
                                        speakers=speakers)
                await message.answer(**content.as_kwargs(),
                                     reply_markup=get_authorized_kb(len(speaker_list)))
            else:
                message.answer('Неверный код')
    else:
        await message.answer('Код может быть только числом')
