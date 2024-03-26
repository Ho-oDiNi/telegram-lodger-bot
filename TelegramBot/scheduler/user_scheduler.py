from aiogram import Bot
from keyboards.user_InlineKeyboards import *
from utils.db_requests import *

async def send_message_month_pay_user(bot: Bot, flat: str):
    
    user_id = db_get_user_id(flat)
    await bot.send_message(chat_id = user_id,
                        text = f"Напоминаем!\nСкоро встреча с администратором\n" +
                        f"Требуется подготовить ежемесячную оплату\n" + 
                        f"Убедительная просьба перед посещением прибраться в квартире",
                        reply_markup = user_builder_admin_username(user_id))
        

async def send_message_communal_pay_user(bot: Bot):
    
    users_id = db_get_users()

    for user_id in users_id:
        await bot.send_message(chat_id = user_id,
                            text = f"Напоминаем!\nСегодня требуется оплатить коммунальные услуги\n",
                            reply_markup = user_builder_admin_username(user_id))
        
async def send_message_change_tariffs_user(bot: Bot):

    users_id = db_get_users()

    for user_id in users_id:
        await bot.send_message(chat_id = user_id,
                            text = f"Напоминаем!\nСегодня смена тарифов коммунальных услуг\n")                