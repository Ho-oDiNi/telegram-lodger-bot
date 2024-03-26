from aiogram import Bot
from keyboards.admin_InlineKeyboards import *
from utils.db_requests import *


async def send_message_month_pay_admin(bot: Bot, flat: str): 

    admin_id = db_get_admin_id(flat)
    await bot.send_message(chat_id = admin_id,
                            text = f"Напоминаем!\nЕжемесячная оплата: {flat}\n"
                            + "Договоритесь о встрече, либо запросите перевод",
                            reply_markup = admin_builder_user_username(flat))
       

async def send_message_communal_pay_admin(bot: Bot, flat: str):

    admin_id = db_get_admin_id(flat)
    await bot.send_message(chat_id = admin_id,
                            text = f"Напоминаем!\nСегодня день оплаты коммунальных услуг\n" +
                                "Проверьте поступление платежей от всех квартир",
                                reply_markup = admin_builder_user_username(flat))
        

async def send_message_change_tariffs_admin(bot: Bot):

    admins_id = db_get_admins()

    for admin_id in admins_id:
        await bot.send_message(chat_id = admin_id,
                            text = f"Напоминаем!\nСегодня смена тарифов коммунальных услуг\n" +
                                    "Требуется внести изменения в гугл таблицах")       

    flats = db_get_flats() 
    for flat in flats:
        bot.google_table.merge_row("Смена тарифов", flat)
        db_merge_row(bot, "Смена тарифов", flat)