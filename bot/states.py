from aiogram.fsm.state import StatesGroup, State


class BaseStates(StatesGroup):
    unauthorized = State()
    code_verification = State()
    authorized = State()
    in_conv = State()
