#Импорты
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.admin_ReplyKeyboards import *
from aiogram.fsm.context import FSMContext
from utils.states import Flat
from keyboards.admin_InlineKeyboards import *
from filters.isAdminFilter import IsAdmin
from filters.isFlatFilter import IsFlat
from utils.format_message import format_str


router = Router()
router.message.filter(IsAdmin())

@router.message(F.text.lower().in_({"назад", "меню"}))     
@router.message(Command("menu","start"))
async def admin_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Flat.flat)
    await message.answer(text=f"Выберете квартиру:", reply_markup=admin_builder_main_menu())


@router.message(Flat.flat, IsFlat())
async def check_flats(message: Message, state: FSMContext):
    try:
        await state.update_data(flat = message.text)
        data = await state.get_data()
        await message.answer(text = f"Выбрана квартира: {data['flat']}", reply_markup=admin_flat_action_keyboard)
    except:
        await message.answer(text = f"Введите /menu")    



@router.message(F.text.lower() == "инфо о квартире")
async def get_info(message: Message, state: FSMContext, bot: Bot):
    try:
        await bot.send_chat_action(message.from_user.id, action="typing")

        data = await state.get_data()
        info = bot.google_table.get_info(data["flat"])

        string = "Информация о квартире:\n"
        for i in info:
            for j in range(2):
                string += format_str(f"{i[j]}", 2)
            string += "\n"

        await message.answer(text = f"<pre>{string}</pre>", reply_markup = admin_builder_flat_url(bot, data["flat"]), parse_mode='html')

    except:
        await message.answer(text = f"Введите /menu")        



@router.message(F.text.lower() == "список оборудования")
async def get_equip(message: Message, state: FSMContext, bot: Bot):
    try:
        await bot.send_chat_action(message.from_user.id, action="typing")

        data = await state.get_data()
        equip = bot.google_table.get_equip(data["flat"])

        string = "<b>Список оборудования:</b>\n"
        for i in equip:
            string += f"{i}\n"
        await message.answer(text = f"{string}", reply_markup = admin_builder_flat_url(bot, data["flat"]), parse_mode='html')
    except:
        await message.answer(text = f"Введите /menu")      


@router.message(F.text.lower() == "журнал счетчиков")
async def log_communal(message: Message, state: FSMContext, bot: Bot):  
    try:            
        await bot.send_chat_action(message.from_user.id, action="typing")

        data = await state.get_data()
        log = db_get_log(bot, data["flat"])
        
        string = f"Дата   Э/П    Г/В    Х/В    Итог\n"
        string += "----------------------------------\n"
        for i in log:
            for j in i:
                string += format_str(f"{j}", 5)
            string += "\n"    

        await message.answer(text = f"<pre>{string}</pre>", reply_markup = admin_builder_flat_url(bot, data["flat"]), parse_mode='html') 
    
    except:
        await message.answer(text = f"Введите /menu")      


@router.message(F.text.lower() == "выселение жильцов")           
async def extraction_request(message: Message):
    try:
        await message.answer(text = f"<b>ВНИМАНИЕ!</b>\n" +
                                "Действие необратимо!\n" + 
                                "Вы уверены?", reply_markup = extraction_keyboard, parse_mode='html') 
    except:
        message.answer(text = f"Список пользователей пуст") 


@router.message(F.text.lower() == "посчитать коммуналку")
async def calculate_communal(message: Message, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        lst = db_get_tariffs()
            
        await message.answer(text = f"<b>Стоимость услуг:</b>\n" + 
                                    f"Э/П:   {lst[0]} р/кВт\n" +              
                                    f"Х/В:   {lst[1]} р/к3\n" + 
                                    f"Г/В:   {lst[2]} р/к3\n" +
                                    f"Сток:  {lst[3]} р/к3\n", parse_mode='html')
        
        await bot.send_chat_action(message.from_user.id, action="typing")

        log = db_get_old_communal(bot, data["flat"])

        string = "Предыдущие значения:\n"                     
        string += f"Дата   Э/П    Г/В    Х/В    Итог\n"
        for i in log:
            string += format_str(f"{i}", 5)
        string += "\n"    

        await message.answer(text = f"<pre>{string}</pre>", parse_mode='html') 


        await state.set_state(Flat.meter)
        await message.answer(text=f"Введите новые значения\n" + 
                                "В любом порядке через пробел:")
        
    except:
        await message.answer(text = f"Введите /menu")

 

@router.message(Flat.meter)
async def check_communal(message: Message, state: FSMContext, bot: Bot):

    await bot.send_chat_action(message.from_user.id, action="typing")

    lst = message.text.split(' ')   

    # Обрабатываем введенные данные
    meters = []
    for item in lst:
        item = item.replace(',', '.')
        item = item.split(".")[0]
        string = str(item)
        if not string.isdigit(): 
            await message.answer("Нецифровые значения\nВведите данные еще раз") 
            return
        meters.append(int(item))
        
    if(len(meters) != 3 ):
        await message.answer("Требуется три значения\nВведите данные еще раз") 
        return   

    meters.sort(reverse=True)

    new_meters = meters

    data = await state.get_data()

    lst_communal = db_get_tariffs()
    old_meters  = db_get_old_communal(bot, data["flat"])[1:4]

    consum = []
    for i in range(3):
        consum.append(meters[i] - old_meters[i])
    consum.append(consum[1] + consum[2])

    #Добавление значений для вывода стока воды
    meters.append(consum[1])
    old_meters.append(consum[2])

    for i in range(3):
        if consum[i] < 0:
            await message.answer("Получились отрицательные значения\nВведите данные еще раз") 
            return
    for i in range(2):    
        if consum[i+1] > 100:
            await message.answer("Получились неестественные значения\nВведите данные еще раз") 
            return
        
    cost = []
    for i in range(4):
        cost.append(consum[i]*lst_communal[i])
        cost[i] = round(cost[i], 2)   

    full_cost = 0
    for i in range(4):
        full_cost = full_cost + cost[i]
    full_cost = round(full_cost, 2) 

    new_meters.append(full_cost)
    await state.update_data(meter = new_meters)

    keys = []
    keys.append(" Э/П | ")
    keys.append("Х/В | ")
    keys.append("Г/В | ")
    keys.append("Сток| ")

    table = [[] * 6 for i in range(4)]
    for i in range(4):
        table[i].append(keys[i])
        table[i].append(meters[i])
        table[i].append(old_meters[i])
        table[i].append(consum[i])
        table[i].append(f"{cost[i]}\n")

    string = "        Наст   Преж  Расход  Сумма\n"
    for i in table:
        for j in i:
            string += format_str(f"{j}", 5)
    string += "-----------------------------------\n"
    string += f"  Итого             =   {full_cost} р"


    await message.answer(text = f"<pre>{string}</pre>", 
                         reply_markup=admin_communal_keyboard, 
                         parse_mode='html')


@router.message(Command("help"))
async def help(message: Message):
    await message.answer( text=f"Бот создан для оповещения уведомлениями об оплате и удобного подсчета коммунальных услуг. Используйте кнопки для навигации")

@router.message()
async def echo(message: Message):
    await message.answer( text=f"Что-то пошло не так...\nПопробуйте ввести /menu")