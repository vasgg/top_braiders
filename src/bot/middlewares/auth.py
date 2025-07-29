from asyncio import create_task
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.enums import Stage
from bot.internal.controllers import blink1, sheet_update
from database.crud.user import add_user_to_db, get_user_from_db_by_tg_id, get_users_count


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        db_session = data["db_session"]
        settings = data["settings"]
        user = await get_user_from_db_by_tg_id(event.from_user.id, db_session)
        if not user:
            user = await add_user_to_db(event.from_user, db_session)
            if settings.bot.stage == Stage.PROD:
                users_count = await get_users_count(db_session)
                create_task(blink1('cyan'))
                create_task(sheet_update('C8', users_count))
        data["user"] = user
        return await handler(event, data)
