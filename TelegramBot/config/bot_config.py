import os
import sqlite3 as sql
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Загрузка переменных окружения
load_dotenv("./config/.env")

# Получение конфигурационных значений
API_TOKEN = os.getenv("API_TOKEN")
GOOGLE_URL = os.getenv("GOOGLE_URL")
ADMIN = os.getenv("ADMIN")

# Валидация обязательных переменных
if not all([API_TOKEN, GOOGLE_URL, ADMIN]):
    raise EnvironmentError("Missing required environment variables")

try:
    ADMIN_ID = int(ADMIN)
except ValueError:
    raise ValueError("ADMIN must be an integer value")

# Инициализация базы данных
DB_PATH = "utils/tg.db"
db = sql.connect(DB_PATH)

# Планировщик задач
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

# Константы
IGNORE_EVENTS = ("заселение", "смена тарифов", "выселение")
