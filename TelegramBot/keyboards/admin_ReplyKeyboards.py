#Импорты
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils.db_requests import db_get_flats


#Клавиатура "Админ Панель главное меню"
def admin_builder_main_menu():

    builder = ReplyKeyboardBuilder()

    flats = db_get_flats()
    for flat in flats:
        builder.button(text=f"{flat}")
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


#Клавиатура "Админ действия с квартирой"
admin_flat_action_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text = "Инфо о квартире"),
            KeyboardButton(text = "Список оборудования"),
        ],
        [
            KeyboardButton(text = "Посчитать коммуналку"),
            KeyboardButton(text = "Журнал счетчиков"),
            KeyboardButton(text = "Выселение жильцов")
        ],
        [
            KeyboardButton(text = "Назад")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Выбирите действие:",
    selective=True
)



