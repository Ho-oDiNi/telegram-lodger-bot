from config.bot_config import  scheduler
from scheduler.admin_scheduler import *
from scheduler.user_scheduler import *
from aiogram import Bot

async def start_scheduler(bot: Bot):

    # Ежемесячная оплата
    pay_day = db_get_dict_pay_day()

    for key in pay_day:
        flat = key
        day = pay_day[f'{key}']
        scheduler.add_job(  send_message_month_pay_admin, 
                        trigger='cron', day = f"{day - 2}, {day}", hour=8,
                        kwargs={"bot": bot, "flat": flat}   )
    for key in pay_day:
        flat = key
        day = pay_day[f'{key}']
        scheduler.add_job(  send_message_month_pay_user, 
                        trigger='cron', day = f"{day - 2}, {day}", hour=8,
                        kwargs={"bot": bot, "flat": flat}   )
        

    # Оплата коммуналки
    communal_day = bot.google_table.get_communal_day() 
    
    flats = db_get_flats()
    for flat in flats:
        scheduler.add_job(  send_message_communal_pay_admin,
                            trigger='cron', day = f"{communal_day - 2}", hour=8,
                            kwargs={"bot": bot, "flat": flat}    )  
        
    scheduler.add_job(  send_message_communal_pay_user,
                        trigger='cron', day = f"{communal_day - 2}", hour=8, 
                        kwargs={"bot": bot}    )  


    # Смена тарифов ЖКХ
    scheduler.add_job(  send_message_change_tariffs_admin,
                        trigger='cron', month = 7, hour=8,
                        kwargs={"bot": bot}    )    
    
    scheduler.add_job(  send_message_change_tariffs_user,
                        trigger='cron', month = 7, hour=8,
                        kwargs={"bot": bot}    )   
    