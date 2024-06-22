from aiogram.fsm.state import StatesGroup, State


class BaseStates(StatesGroup):
    """
    Класс состояний для управления состояниями FSM.

    Состояния:
        unauthorized: Состояние для неавторизованных пользователей.
        code_verification: Состояние для проверки кода.
        authorized: Состояние для авторизованных пользователей.
        in_conv: Состояние для взаимодействия с устройством.
    """
    unauthorized = State()
    code_verification = State()
    authorized = State()
    in_conv = State()
