from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils.db_requests import *

class IsFlat(BaseFilter):
    async def __call__(self, message: Message) -> bool:

        flats = db_get_flats()

        if message.text in flats:
            return True
        
        return False