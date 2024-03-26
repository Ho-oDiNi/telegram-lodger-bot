from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.db_requests import *

admin_communal_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text = "Внести изменения", callback_data="calculate_communal")
        ],
        [
            InlineKeyboardButton(text = "Не вносить", callback_data="None")
        ]
    ]
)

extraction_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text = "Выселить", callback_data="extraction_agree")
        ],
        [
            InlineKeyboardButton(text = "Отмена", callback_data="None")
        ]
    ]
)

merge_row_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text = "Добавить", callback_data="merge_row_agree")
        ],
        [
            InlineKeyboardButton(text = "Отмена", callback_data="login_disagree")
        ]
    ]
)

login_user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text = "Разрешить", callback_data="login_agree")
        ],
        [
            InlineKeyboardButton(text = "Запретить", callback_data="login_disagree")
        ]
    ]
)

def admin_builder_user_username(flat:str):

    user_id = db_get_user_id(flat)

    builder = InlineKeyboardBuilder()
    builder.button(text="Связаться с жильцом", url = f"tg://user?id={user_id}")

    return builder.as_markup()


def admin_builder_flat_url(bot:Bot, flat_name:str):
    wks_url = bot.google_table.get_wks_url(flat_name)

    builder = InlineKeyboardBuilder()
    builder.button(text="Открыть в таблице", url = wks_url)

    return builder.as_markup()
