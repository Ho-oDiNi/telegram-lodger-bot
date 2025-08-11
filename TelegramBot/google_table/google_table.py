from config.bot_config import GOOGLE_URL, IGNORE_EVENTS
import pygsheets
import datetime
from typing import List, Tuple, Union

class GoogleTable:
    def __init__(
        self, 
        credence_service_file: str = "config/google_config.json", 
        googlesheet_file_url: str = GOOGLE_URL
    ) -> None:
        self.credence_service_file = credence_service_file
        self.googlesheet_file_url = googlesheet_file_url
        self._client = None  # Кэширование клиента

    @property
    def client(self) -> pygsheets.client.Client:
        """Кэшированный клиент Google Sheets."""
        if self._client is None:
            self._client = pygsheets.authorize(
                service_file=self.credence_service_file
            )
        return self._client

    def _get_worksheet(self, sheet_name: str) -> pygsheets.Worksheet:
        """Получает рабочий лист по имени."""
        spreadsheet = self.client.open_by_url(self.googlesheet_file_url)
        return spreadsheet.worksheet_by_title(sheet_name)

    # ----------------- Вспомогательные функции ----------------- #

    @staticmethod
    def format_cell(column: str, row: int) -> str:
        """Форматирует адрес ячейки."""
        return f"{column}{row}"

    def get_k_flats(self) -> int:
        """Возвращает количество квартир."""
        wks = self._get_worksheet("botInfo")
        return int(wks.get_value(self.format_cell("A", 2)))

    def get_k_users(self) -> int:
        """Возвращает количество пользователей."""
        wks = self._get_worksheet("botInfo")
        return int(wks.get_value(self.format_cell("A", 3)))

    def get_row_communal(self, sheet_name: str) -> int:
        """Возвращает текущую строку для показаний."""
        wks = self._get_worksheet(sheet_name)
        return int(wks.get_value(self.format_cell("J", 1)))

    # ----------------- Функции для баз данных ----------------- #

    def get_flats_db(self) -> List[list]:
        """Получает данные о квартирах для БД."""
        wks = self._get_worksheet("botInfo")
        k_flats = self.get_k_flats()
        
        start = self.format_cell("C", 2)
        end = self.format_cell("E", k_flats + 1)
        
        return wks.get_values(start, end)

    def get_users_db(self) -> List[list]:
        """Получает данные о пользователях для БД."""
        wks = self._get_worksheet("botInfo")
        k_users = self.get_k_users()
        
        start = self.format_cell("F", 2)
        end = self.format_cell("G", k_users + 1)
        
        try:
            return wks.get_values(start, end)
        except Exception:
            return []

    # ----------------- Функции показаний счетчиков ----------------- #

    def get_tariffs(self) -> List[float]:
        """Возвращает текущие тарифы ЖКХ."""
        wks = self._get_worksheet("botInfo")
        
        start = self.format_cell("B", 10)
        end = self.format_cell("B", 13)
        
        values = wks.get_values(start, end)
        return [float(v[0].replace(',', '.')) for v in values]

    def set_new_communal(self, sheet_name: str, meters: list) -> None:
        """Записывает новые показания счетчиков."""
        wks = self._get_worksheet(sheet_name)
        row = self.get_row_communal(sheet_name) + 1
        
        # Форматирование даты
        now = datetime.datetime.now()
        date_str = now.strftime("%d.%m.%y")
        
        # Обновление значений за один запрос
        update_data = [
            (f"A{row}", date_str),
            (f"B{row}", meters[0]),
            (f"G{row}", meters[1]),
            (f"L{row}", meters[2])
        ]
        
        for cell, value in update_data:
            wks.cell(cell).set_value(value)

    def get_log(self, sheet_name: str, row_start: int = -1) -> List[list]:
        """Получает журнал показаний."""
        wks = self._get_worksheet(sheet_name)
        current_row = self.get_row_communal(sheet_name)
        
        start_row = 10 if row_start == -1 else current_row - row_start
        end_row = current_row
        
        start = self.format_cell("A", start_row)
        end = self.format_cell("T", end_row)
        
        data = wks.get_values(start, end)
        log = []
        
        for row in data:
            # Обработка специальных событий
            if row[0].lower() in IGNORE_EVENTS:
                log.append([row[0].lower(), 0, 0, 0, 0])
                continue
            
            # Форматирование даты
            date_str = row[0][:5] if len(row[0]) > 5 else row[0]
            
            # Извлечение значений
            try:
                electro = int(row[1]) if row[1] else 0
                cold = int(row[6]) if row[6] else 0
                hot = int(row[11]) if row[11] else 0
                total = float(row[19].replace(',', '.')) if row[19] else 0.0
            except (ValueError, TypeError):
                electro = cold = hot = total = 0
                
            log.append([date_str, electro, cold, hot, total])
        
        return log

    # ----------------- Информация о квартире ----------------- #

    def get_info(self, sheet_name: str) -> List[list]:
        """Получает информацию о квартире."""
        wks = self._get_worksheet(sheet_name)
        start = self.format_cell("V", 2)
        end = self.format_cell("W", 7)
        return wks.get_values(start, end)

    def get_equip(self, sheet_name: str) -> List[str]:
        """Получает список оборудования."""
        wks = self._get_worksheet(sheet_name)
        
        # Получаем количество позиций оборудования
        try:
            row_equip = int(wks.get_value("W8"))
        except (ValueError, TypeError):
            row_equip = 0
        
        if row_equip <= 0:
            return []
        
        start = self.format_cell("Y", 2)
        end = self.format_cell("Y", row_equip + 1)
        
        values = wks.get_values(start, end)
        return [item[0] for item in values] if values else []

    # ----------------- Операции с пользователями ----------------- #

    def login_agree(self, user_id: Union[int, str], flat: str) -> None:
        """Регистрирует нового пользователя."""
        wks = self._get_worksheet("botInfo")
        row = self.get_k_users() + 2
        
        # Обновление в одном запросе
        wks.update_values(
            f"F{row}:G{row}", 
            [[str(user_id), flat]]
        )

    def extraction_agree(self, flat: str) -> None:
        """Удаляет пользователей квартиры."""
        wks = self._get_worksheet("botInfo")
        k_users = self.get_k_users()
        
        start = self.format_cell("F", 2)
        end = self.format_cell("G", k_users + 1)
        
        data = wks.get_values(start, end)
        
        # Фильтрация пользователей
        filtered_data = [
            [user_id, user_flat] 
            for user_id, user_flat in data 
            if user_flat != flat
        ]
        
        # Дополнение пустыми значениями
        while len(filtered_data) < k_users:
            filtered_data.append(["", ""])
        
        # Разделение на колонки
        user_ids = [row[0] for row in filtered_data]
        flats = [row[1] for row in filtered_data]
        
        wks.update_col(6, user_ids, 2)  # Колонка F
        wks.update_col(7, flats, 2)     # Колонка G

    def get_wks_url(self, sheet_name: str) -> str:
        """Возвращает URL рабочего листа."""
        return self._get_worksheet(sheet_name).url

    # ----------------- Функции планировщика ----------------- #

    def get_communal_day(self) -> int:
        """Возвращает день оплаты коммунальных услуг."""
        wks = self._get_worksheet("botInfo")
        return int(wks.get_value(self.format_cell("B", 2)))

    # ----------------- Форматирование данных ----------------- #

    def merge_row(self, event_type: str, sheet_name: str) -> None:
        """Объединяет ячейки для события."""
        wks = self._get_worksheet(sheet_name)
        row = self.get_row_communal(sheet_name) + 1
        
        # Установка значения и объединение
        wks.cell(f"A{row}").set_value(event_type)
        wks.merge_cells(
            f"A{row}", 
            f"T{row}", 
            merge_type=pygsheets.MergeType.MERGE_ALL
        )
