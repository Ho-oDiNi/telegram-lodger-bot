from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils.db_requests import *

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        
        admins_id = db_get_admins()

        if message.from_user.id in admins_id:
            return True
        
        return False