#Импорты
from dotenv import dotenv_values
import sqlite3 as sql
from apscheduler.schedulers.asyncio import AsyncIOScheduler

#Получение токена из файла .env
config = dotenv_values('./config/.env')
API_TOKEN = config['API_TOKEN']
GOOGLE_URL = config['GOOGLE_URL']
ADMIN = int(config['ADMIN'])

db = sql.connect("utils/tg.db")


scheduler = AsyncIOScheduler(timezone = "Europe/Moscow")

IGNORE_DATE = ('заселение', 'смена тарифов','выселение')