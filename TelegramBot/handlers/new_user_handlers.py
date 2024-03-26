#Импорты
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from keyboards.admin_InlineKeyboards import login_user_keyboard
from aiogram.fsm.context import FSMContext
from utils.states import Login
from filters.isFlatFilter import IsFlat
from utils.db_requests import *

router = Router()                                

#Хендлер реагирует на комманду старт.
@router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    await message.answer(text=f"Для входа в систему требуется ввести адрес квартиры")
    await state.set_state(Login.street)
    await message.answer(text=f"Введите улицу с большой буквы: ")

@router.message(Login.street, IsFlat())
async def login_street(message: Message, state: FSMContext):
    await state.update_data(street = message.text)
    await state.set_state(Login.apartment)
    await message.answer(text=f"Введите номер квартиры: ")

@router.message(Login.street)
async def incorrect_login_street(message: Message, state: FSMContext):
    await message.answer(text=f"Введите улицу еще раз: ")

@router.message(Login.apartment, F.text.isdigit())
async def login_apartment(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(apartment = message.text)
    data = await state.get_data()
    await state.clear()

    user_id = message.from_user.id
    street = data['street']

    admin_id = db_new_user_login(user_id, street)

    await bot.send_message(chat_id = admin_id,
                            text = f"Пользователь @{message.from_user.username} пытается получить доступ\nк {data['street']} {data['apartment']}\n",
                            reply_markup = login_user_keyboard)

    await message.answer(text=f"Информация для авторизации отправлена админу")  

    
@router.message(Command("help"))
async def help(message: Message):
    await message.answer( text=f"Бот создан для оповещения уведомлениями об оплате и удобного подсчета коммунальных услуг. Используйте кнопки для навигации")

@router.message()
async def echo(message: Message):
    await message.answer( text=f"Введите данные и дождитесь ответа администратора ;)")



