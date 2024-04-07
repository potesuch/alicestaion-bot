from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_authorized_kb(speaker_cnt) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for i in range(speaker_cnt):
        kb.add(KeyboardButton(text=str(i+1)))
    kb.adjust(4)
    kb.row(KeyboardButton(text='Выйти из аккаунта'))
    return kb.as_markup(resize_keyboard=True)
