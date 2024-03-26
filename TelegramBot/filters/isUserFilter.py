from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils.db_requests import *

class IsUser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        
        users_id = db_get_users()

        if message.from_user.id in users_id:
            return True
        
        return False