from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_conversation_kb() -> ReplyKeyboardMarkup:
    """
    Возвращает клавиатуру для режима общения с устройством.
    """
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text='Выход'))
    return kb.as_markup(resize_keyboard=True)
