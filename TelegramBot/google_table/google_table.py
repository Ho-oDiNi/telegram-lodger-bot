from config.bot_config import GOOGLE_URL, IGNORE_DATE
import pygsheets
import datetime

class GoogleTable:
    
    def __init__(
        self, credence_service_file:str = "config/google_config.json", googlesheet_file_url:str = GOOGLE_URL
    ) -> None:
        self.credence_service_file = credence_service_file
        self.googlesheet_file_url = googlesheet_file_url

    def _get_googlesheet_by_url(
        self, googlesheet_client: pygsheets.client.Client, sheet_name:str
    ) -> pygsheets.Spreadsheet:
        sheets: pygsheets.Spreadsheet = googlesheet_client.open_by_url(
            self.googlesheet_file_url
        )
        return sheets.worksheet_by_title(sheet_name)

    def _get_googlesheet_client(self):
        return pygsheets.authorize(
            service_file=self.credence_service_file
        )

#  - - - - - - - - - - - - - Вспомогательные функции - - - - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Удобное форматирование ячейки
    def Cell(self, column:str, row):
        return column + str(row)
    
    # Количество квартир
    def get_k_flats(self):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, "botInfo")  

        cell = self.Cell("A", 2)
        k_flats = int(wks.get_value(cell))

        return k_flats    
    
    # Количество пользователей
    def get_k_users(self):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, "botInfo")  

        cell = self.Cell("A", 3)
        k_users = int(wks.get_value(cell))

        return k_users 

    # Номер строки в таблице счетчиков
    def get_row_communal(self, sheet_name:str):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, sheet_name)  

        cell = self.Cell("J", 1)
        row = int(wks.get_value(cell))

        return row 


#  - - - - - - - - - - - - - Фунции для баз данных  - - - - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Считывание квартир для ввода в БД
    def get_flats_db(self):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, "botInfo")       

        k_flats = self.get_k_flats()

        cell_start = self.Cell("C", 2)
        cell_end = self.Cell("E", k_flats + 1)

        lst = wks.get_values(cell_start, cell_end)

        return lst
    
    # Считывание пользователей для ввода в БД
    def get_users_db(self):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, "botInfo")       

        k_users = self.get_k_users()

        cell_start = self.Cell("F", 2)
        cell_end = self.Cell("G", k_users + 1)

        try:
            lst = wks.get_values(cell_start, cell_end)
        except:
            lst = []

        return lst
    

#  - - - - - - - - - - - - - Функции показаний счетчиков  - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Тарифы ЖКХ
    def get_tariffs(self):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, "botInfo")      

        cell_start = self.Cell("B", 10)
        cell_end = self.Cell("B", 13)

        lst = wks.get_values(cell_start, cell_end)

        # Форматирование значений из таблицы
        lst_communal = []
        for i in lst:
            for j in i:
                lst_communal.append(float(j.replace(',', '.')))

        return lst_communal

    # МОЖНО СДЕЛАТЬ АСИНХРОННОЙ?
    # Запись новых показаний счетчиков в таблицу
    def set_new_communal(self, sheet_name:str, meters):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, sheet_name) 

        # Сегодняшняя дата
        current_time = datetime.datetime.now()
        date = f"{str(current_time.day).zfill(2)}.{str(current_time.month).zfill(2)}.{str(current_time.year)[2:]}"
        row = self.get_row_communal(sheet_name) + 1

        cell_date = wks.cell(f"A{row}")
        cell_date.set_value(date)

        cell_electro = wks.cell(f"B{row}")
        cell_electro.set_value(meters[0])

        cell_cold = wks.cell(f"G{row}")
        cell_cold.set_value(meters[1])

        cell_hot = wks.cell(f"L{row}")
        cell_hot.set_value(meters[2])

        return

    def get_log(self, sheet_name:str, row_start = -1):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, sheet_name) 

        row = self.get_row_communal(sheet_name)

        if row_start == -1:
            cell_start = self.Cell("A", 10)     
        else:    
            cell_start = self.Cell("A", row - row_start)
        cell_end = self.Cell("T", row)

        lst = wks.get_values(cell_start, cell_end)

        # Форматируем данные
        for i in range(len(lst)):
            for j in range(20):
                lst[i][j] = lst[i][j].replace(',', '.')

        log = [[] * 6 for i in range(len(lst))]

        for i in range(len (lst)):

            if (lst[i][0].lower() in IGNORE_DATE):
                log[i] = [lst[i][0].lower(), 0, 0, 0, 0]
                continue

            if(len(lst[i][0]) > 5 ):
                date = lst[i][0]
                lst[i][0] = date[:5]

            log[i].append(lst[i][0])
            log[i].append(int(lst[i][1]))
            log[i].append(int(lst[i][6]))
            log[i].append(int(lst[i][11]))
            log[i].append(float(lst[i][19]))

        return log

#  - - - - - - - - - -  Различная информация о квартире - - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Информация о квартире
    def get_info(self, sheet_name:str):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, sheet_name) 

        cell_start = self.Cell("V", 2)
        cell_end = self.Cell("W", 7)

        lst = wks.get_values(cell_start, cell_end)

        return lst

    # Список оборудования
    def get_equip(self, sheet_name:str):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, sheet_name) 

        row_equip = int(wks.get_value("W8"))

        cell_start = self.Cell("Y", 2)
        cell_end = self.Cell("Y", row_equip + 1)

        lst = wks.get_values(cell_start, cell_end)     

        # Форматирование данных
        equip = []
        for i in lst:
            for j in i:
                equip.append(j)

        return equip    


#  - - - - - - - - - -  Функции Inline клавиатур  - - - - - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # МОЖНО СДЕЛАТЬ АСИНХРОННОЙ?
    # Запись нового пользователя в таблицу
    def login_agree(self, user_id, flat):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, "botInfo") 

        row = self.get_k_users() + 2

        cell_user_id = wks.cell(f"F{row}")
        cell_user_id.set_value(user_id)

        cell_flat = wks.cell(f"G{row}")
        cell_flat.set_value(flat)

        return

    # МОЖНО СДЕЛАТЬ АСИНХРОННОЙ?
    # Выселение пользователей
    def extraction_agree(self, flat:str):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, "botInfo") 

        k_users = self.get_k_users()

        cell_start = self.Cell("F", 2)
        cell_end = self.Cell("G", k_users + 1)

        lst = wks.get_values(cell_start, cell_end)

        # Создаем новый список пользователей
        new_users_column = []
        new_flat_column = []
        for i in lst:
            if i[1] != flat:
                new_users_column.append(i[0])
                new_flat_column.append(i[1])

        # Добавляем пустые ячейки вместо удаленных записей
        for i in range(len(lst) - len(new_users_column)):
            new_users_column.append("")
            new_flat_column.append("")

        wks.update_col("F", new_users_column, 1)
        wks.update_col("G", new_flat_column, 1)
            
        return               

    # Получить ссылку на таблицу по имени
    def get_wks_url(self, sheet_name:str):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, sheet_name) 

        return wks.url

#  - - - - - - - - - -  Функции scheduler - - - - - - - - - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # Получить день оплаты коммунальных услуг
    def get_communal_day(self):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, "botInfo") 

        cell = self.Cell("B", 2)
        communal_day = int(wks.get_value(cell))

        return communal_day

#  - - - - - - - - - -  Функции форматирования данных - - - - - - - - - - - - - - - #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #    

    # МОЖНО СДЕЛАТЬ АСИНХРОННОЙ?
    def merge_row(self, string, sheet_name:str):
        googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
        wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client, sheet_name) 

        row = self.get_row_communal(sheet_name) + 1

        cell_start = self.Cell("A", row)
        cell_end = self.Cell("T", row)

        cell_date = wks.cell(f"A{row}")
        cell_date.set_value(string)

        rng = wks.get_values(cell_start, cell_end, returnas='range')
        rng.merge_cells()

        return