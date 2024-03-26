from config.bot_config import db, IGNORE_DATE
from aiogram import Bot
import datetime

#  - - - - - - - - - - - - Функции создания/удаления таблиц - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Создание таблиц
def db_creates_tables():

    cur = db.cursor()

    cur.execute("DROP TABLE IF EXISTS db_flats")
    cur.execute("CREATE TABLE db_flats("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "flat TEXT, "
                "admin_id INTEGER, "
                "pay_day INTEGER)"
    )
    
    cur.execute("DROP TABLE IF EXISTS db_users")
    cur.execute("CREATE TABLE IF NOT EXISTS db_users("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_id INTEGER, "
                "flat TEXT)"
    )

    cur.execute("DROP TABLE IF EXISTS db_login_user")
    cur.execute("CREATE TABLE IF NOT EXISTS db_login_user("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "user_id INTEGER, "
                "flat TEXT)"
    )

    cur.execute("DROP TABLE IF EXISTS db_communal_tariffs")
    cur.execute("CREATE TABLE IF NOT EXISTS db_communal_tariffs("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "electro_cost REAL, "
                "cold_water_cost REAL, "
                "hot_water_cost REAL, "
                "stock_water_cost REAL)"
    )

    cur.execute("DROP TABLE IF EXISTS db_communal_log")
    cur.execute("CREATE TABLE IF NOT EXISTS db_communal_log("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "date TEXT, "
                "electro INTEGER, "
                "cold_water INTEGER, "
                "hot_water INTEGER, "
                "total_cost REAL, "
                "flat TEXT)"
    )

    db.commit()

# Заполнение таблиц
def db_insert_tables(bot: Bot):

    cur = db.cursor()

    db_flats = bot.google_table.get_flats_db()
    db_users = bot.google_table.get_users_db()

    for i in db_flats:
        cur.execute(f"INSERT INTO db_flats (flat, admin_id, pay_day) VALUES ('{i[0]}', {i[1]}, {i[2]})")

    for i in db_users:
        cur.execute(f"INSERT INTO db_users (user_id, flat) VALUES ({i[0]}, '{i[1]}')")

    lst = bot.google_table.get_tariffs()
    cur.execute(f"INSERT INTO db_communal_tariffs (electro_cost, cold_water_cost, hot_water_cost, stock_water_cost) VALUES ({lst[0]}, {lst[1]}, {lst[2]}, {lst[3]})")

    for i in db_flats:
        flat = i[0]
        lst = bot.google_table.get_log(flat)

        for j in lst:
            cur.execute(f"INSERT INTO db_communal_log (date, electro, cold_water, hot_water, total_cost, flat) VALUES ('{j[0]}', {j[1]}, {j[2]}, {j[3]}, '{j[4]}', '{flat}')")

    db.commit()
    
# Удаление таблиц
def db_drop_tables():
    cur = db.cursor()

    cur.execute("DROP TABLE db_flats")
    cur.execute("DROP TABLE db_users")
    cur.execute("DROP TABLE db_login_user")
    cur.execute("DROP TABLE db_communal_tariffs")
    cur.execute("DROP TABLE db_communal_log")

    db.commit()

#  - - - - - - - - - Функции добавления/удаления пользователя - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
# Создание записи о новом пользователе
def db_new_user_login(user_id: int, street: str) -> int:

    cur = db.cursor()

    cur.execute(f"INSERT INTO db_login_user (user_id, flat) VALUES ({user_id}, '{street}' )")
    request = cur.execute(f"SELECT admin_id FROM db_flats WHERE flat = '{street}' ").fetchone()
    admin_id = int(request[0])

    db.commit()

    return admin_id

# Очистка бд
def db_delete_login_users():
    cur = db.cursor()
    cur.execute(f"DELETE FROM db_login_user WHERE id > 0")
    db.commit()


# Информация о новом пользователе
def db_get_new_user_login():
    cur = db.cursor()

    request = cur.execute(f"SELECT * FROM db_login_user").fetchone()
    user_id = int(request[1])
    flat = request[2]

    return user_id, flat


# Доделать во второй версии
# Добавление нового пользователя
def db_agree_user_login():

    cur = db.cursor()

    user_id, flat = db_get_new_user_login()

    cur.execute(f"INSERT INTO db_users (user_id, flat) VALUES ({user_id}, '{flat}')")

    db.commit()

    

# Удалить пользователей по квартире
def db_extraction_users(flat:str):
    cur = db.cursor()

    cur.execute(f"DELETE FROM db_users WHERE flat = '{flat}' ")  
    
    db.commit()

    
#  - - - - - - - - - Функции получения всех записей - - - - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Получить все квартиры
def db_get_flats():

    cur = db.cursor()

    flat = cur.execute("SELECT flat FROM db_flats").fetchall()
    flats = []
    for i in flat:
        for j in i:
            flats.append(j)

    return flats

# Получить всех админов
def db_get_admins():

    cur = db.cursor()

    tg_id = cur.execute("SELECT admin_id FROM db_flats").fetchall()
    admins_id = []
    for i in tg_id:
        for j in i:
            admins_id.append(int(j))
    
    return set(admins_id)

# Получить всех пользователей
def db_get_users():

    cur = db.cursor()

    tg_id = cur.execute("SELECT user_id FROM db_users").fetchall()
    users_id = []
    for i in tg_id:
        for j in i:
            users_id.append(int(j))

    return users_id


#  - - - - - - - - - Функции запроса по параметру - - - - - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Получить id админа по квартире
def db_get_admin_id(flat: str):

    cur = db.cursor()  
    request = cur.execute(f"SELECT admin_id FROM db_flats WHERE flat = '{flat}' ").fetchone()
    admin_id = request[0]

    return admin_id

# Получить id пользователя по квартире
def db_get_user_id(flat: str):

    cur = db.cursor()  
    request = cur.execute(f"SELECT user_id FROM db_users WHERE flat = '{flat}' ").fetchone()
    user_id = request[0]

    return user_id


# Получить квартиру по id пользователя
def db_get_user_flat(user_id: int):

    cur = db.cursor()  

    request = cur.execute(f"SELECT flat FROM db_users WHERE user_id = {user_id} ").fetchone()

    flat = request[0]

    return flat


#  - - - - - - - - - -  Функции показаний счетчиков - - - - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#Показания счетчиков
def db_get_tariffs():

    cur = db.cursor()  

    request = cur.execute(f"SELECT * FROM db_communal_tariffs").fetchone()

    return list(request[1:])


#Показания совпадения гугл и бд таблиц
def db_check_current_row(bot: Bot, flat:str):

    cur = db.cursor() 
    request = cur.execute(f"SELECT count(*) FROM db_communal_log WHERE flat = '{flat}' ").fetchone()

    db_row = request[0]
    ggl_row = bot.google_table.get_row_communal(flat) - 9

    if ggl_row > db_row:
        log = bot.google_table.get_log(flat, ggl_row - db_row - 1)

        for i in log:
            i.append(f'{flat}')
            new_log = tuple(i)
            cur.execute(f"INSERT INTO db_communal_log (date, electro, cold_water, hot_water, total_cost, flat) VALUES {new_log}")
   
    if ggl_row < db_row:
        for i in range(db_row - ggl_row):
            cur.execute(f"DELETE FROM db_communal_log WHERE id = (SELECT MAX(id) FROM db_communal_log)")

    db.commit()

    return

# Прошлые показания
def db_get_old_communal(bot: Bot, flat:str):
    
    db_check_current_row(bot, flat)

    cur = db.cursor()  

    request = str(  "SELECT * FROM db_communal_log WHERE id = "+
                    "(SELECT MAX(id) FROM db_communal_log "+ 
                    f"WHERE flat = '{flat}' AND date NOT IN {IGNORE_DATE})")
    
    old_meters = cur.execute(request).fetchone()


    return list(old_meters[1:6])


# Журнал счетчиков
def db_get_log(bot: Bot, flat:str, user_mod = False):
    
    db_check_current_row(bot, flat)

    cur = db.cursor()  
    request = cur.execute(f"SELECT * FROM db_communal_log WHERE flat = '{flat}' ORDER BY id DESC LIMIT 5").fetchall()

    if user_mod:
        for i in range(len(request)):
            if request[i][1] in IGNORE_DATE:
                request = request[:i+1]
                break

    log = [[] * 6 for i in range(len(request))]
    log_len = len(log)

    for i in range(log_len):
        for j in range(1, 6):
            log[i].append(request[(log_len-1) - i][j])

    return log

# Добавление новых показаний
def db_set_new_communal(bot: Bot, flat, meters):

    db_check_current_row(bot, flat)

    cur = db.cursor()  

    # Сегодняшняя дата
    current_time = datetime.datetime.now()
    date = f"{str(current_time.day).zfill(2)}.{str(current_time.month).zfill(2)}"

    cur.execute(f"INSERT INTO db_communal_log (date, electro, cold_water, hot_water, total_cost, flat) VALUES ('{date}', {meters[0]}, {meters[1]}, {meters[2]}, '{meters[3]}', '{flat}')")

    db.commit()

    return


def db_merge_row(bot: Bot, string, flat):

    db_check_current_row(bot, flat)

    cur = db.cursor()
    cur.execute(f"INSERT INTO db_communal_log (date, electro, cold_water, hot_water, total_cost, flat) VALUES ('{string.lower()}', {0}, {0}, {0}, '{0}', '{flat}')")
    db.commit()

    return


#  - - - - - - - - - -  Функции scheduler - - - - - - - - - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Получить день ежемесячной оплаты
def db_get_dict_pay_day():

    cur = db.cursor()  

    request = cur.execute(f"SELECT flat, pay_day FROM db_flats").fetchall()

    pay_day = {}
    for i in request:
        pay_day[f'{i[0]}'] = i[1]

    return pay_day



