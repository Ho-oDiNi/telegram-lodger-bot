#Импорты
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from filters.isUserFilter import IsUser
from keyboards.user_ReplyKeyboards import *
from utils.db_requests import *
from utils.states import User_problem
from utils.format_message import format_str

router = Router()                                
router.message.filter(IsUser())

@router.message(F.text.lower().in_({"назад", "меню"}))       
@router.message(Command("menu", "start"))
async def menu(message: Message):
    await message.answer( text=f"Выбирите действие:", reply_markup=user_main_menu_keyboard)


@router.message(F.text.lower() == "инфо о квартире")
async def get_info(message: Message, bot: Bot):

    await bot.send_chat_action(message.from_user.id, action="typing")

    flat = db_get_user_flat(message.from_user.id)
    info = bot.google_table.get_info(flat)

    string = "Информация о квартире:\n"
    for i in info:
        for j in range(2):
            string += format_str(f"{i[j]}", 2)
        string += "\n"

    await message.answer(text = f"<pre>{string}</pre>", parse_mode='html')

  
@router.message(F.text.lower() == "журнал счетчиков")
async def log_communal(message: Message, bot: Bot):  

    await bot.send_chat_action(message.from_user.id, action="typing")                      

    flat = db_get_user_flat(message.from_user.id)
    lst = db_get_tariffs()
            
    await message.answer(text = f"<b>Стоимость услуг:</b>\n" + 
                                f"Э/П:   {lst[0]} р/кВт\n" +              
                                f"Х/В:   {lst[1]} р/к3\n" + 
                                f"Г/В:   {lst[2]} р/к3\n" +
                                f"Сток:  {lst[3]} р/к3\n", parse_mode='html')

    log = db_get_log(bot, flat, True)
    string = f"Дата   Э/П    Г/В    Х/В    Итог\n"
    string += "----------------------------------\n"
    for i in log:
        for j in i:
            string += format_str(f"{j}", 5)
        string += "\n"  
          
    await message.answer(text = f"<pre>{string}</pre>", parse_mode='html') 


@router.message(F.text.lower() == "сообщить о проблеме")
async def report_problem(message: Message, state: FSMContext, bot: Bot):                        

    await state.set_state(User_problem.problem)
    await message.answer( text=f"Опишите проблему\nОна автоматически отправится администратору", reply_markup = user_back_to_menu_keyboard)

# Добавить подтверждение
@router.message(User_problem.problem)
async def confirm_problem(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(problem = message.text)
    await state.set_state(User_problem.confirm)
    await message.answer(text=f"Подтвердите отправку сообщения:\n{message.text}", reply_markup = user_confirm_keyboard)


@router.message(User_problem.confirm)
async def send_report(message: Message, state: FSMContext, bot: Bot):
    if(message.text.lower() == "отмена"):
        await message.answer(text=f"Действие отменено", reply_markup=user_main_menu_keyboard)
        await state.clear()
        return
    
    elif(message.text.lower() == "отправить"):
        await state.update_data(confirm = message.text)
        data = await state.get_data()
        await state.clear()

        flat = db_get_user_flat(message.from_user.id)
        admin_id = db_get_admin_id(flat)

        await bot.send_message(chat_id = admin_id, 
                                text = f"Пользователь @{message.from_user.username} ({flat}) просит помощи:\n{data['problem']}\n")

        await message.answer(text=f"Информация отправлена админу", reply_markup=user_main_menu_keyboard)

    else:
        await message.answer(text=f"Действие отменено", reply_markup=user_main_menu_keyboard)
        await state.clear()

@router.message()
async def echo(message: Message):
    await message.answer( text=f"Что-то пошло не так...\nПопробуйте ввести /menu")