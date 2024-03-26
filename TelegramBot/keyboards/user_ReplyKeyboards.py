#Импорты
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton

user_main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "Инфо о квартире"),
        ],
        [
            KeyboardButton(text = "Журнал счетчиков"),
        ],
        [
            KeyboardButton(text = "Сообщить о проблеме"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Выбирите действие:",
    selective=True
)

user_back_to_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "Назад"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True
)

user_confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "Отправить"),
            KeyboardButton(text = "Отмена"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True
)
