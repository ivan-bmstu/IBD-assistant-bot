import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import SimpleEventIsolation

from bot.handlers import main_handler, bowel_movement
from bot.middlewares import DatabaseMiddleware
from bot.middlewares.error_handler import ErrorHandlerMiddleware
from bot.middlewares.fsm_destiny import DestinyMiddleware
from bot.middlewares.patched_fsm import PatchedFSMContextMiddleware
from config.settings import settings
from database.fsm_storage import PostgresStorage
from database.session import engine

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot"""
    logger.info("Starting Poop Tracker Bot...")

    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = PostgresStorage(engine=engine)
    dp = Dispatcher(
        storage=storage,
        events_isolation=SimpleEventIsolation(),
        disable_fsm=True
    )

    # Register middlewares
    dp.update.outer_middleware(ErrorHandlerMiddleware())
    dp.update.outer_middleware(DestinyMiddleware(storage))
    dp.update.outer_middleware(PatchedFSMContextMiddleware(storage, events_isolation=SimpleEventIsolation()))
    dp.update.middleware(DatabaseMiddleware())

    # Register routers
    dp.include_router(bowel_movement.router)
    dp.include_router(main_handler.router)

    # Start bot
    logger.info("Bot started successfully")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
