from typing import Any

from aiogram import Bot
from aiogram.fsm.middleware import FSMContextMiddleware
from aiogram.fsm.storage.base import DEFAULT_DESTINY
from aiogram.types import TelegramObject


class PatchedFSMContextMiddleware(FSMContextMiddleware):
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        bot: Bot = data["bot"]
        destiny = data.get("destiny", DEFAULT_DESTINY)
        context = self.resolve_event_context(bot, data, destiny=destiny)
        data["fsm_storage"] = self.storage
        if context:
            # Bugfix: https://github.com/aiogram/aiogram/issues/1317
            # State should be loaded after lock is acquired
            async with self.events_isolation.lock(key=context.key):
                data.update({"state": context, "raw_state": await context.get_state()})
                return await handler(event, data)
        return await handler(event, data)
