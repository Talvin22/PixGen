from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from Admin.config import ADMIN_ID


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        admin_ids = ADMIN_ID
        return message.from_user.id in admin_ids
