from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.db_requests import *

def user_builder_admin_username(user_id:int):

    flat = db_get_user_flat(user_id)
    admin_id = db_get_admin_id(flat)

    builder = InlineKeyboardBuilder()
    builder.button(text="Связаться с администратором", url = f"tg://user?id={admin_id}")

    return builder.as_markup()
