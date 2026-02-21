import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Middleware to handle errors in handlers and other middlewares.
    """

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception("Cause exception: %s", e)

            # Try to answer user that something went wrong
            message = getattr(event, "message", None)
            if message and message.chat.id:
                await message.bot.send_message(
                    chat_id=message.chat.id,
                    text="Что-то пошло не так. Попробуйте еще раз позже."
                )
            return None  # Stop event propagation
