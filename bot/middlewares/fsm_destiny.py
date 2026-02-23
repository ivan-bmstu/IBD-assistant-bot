from aiogram import BaseMiddleware
from aiogram.fsm.storage.base import StorageKey

from bot.handlers.bowel_movement import BowelMovementStates
from bot.handlers.constants import BowelMovementMessageCommand, BowelMovementCallbackKey, MainCallbackKey

BOWEL_MOVEMENT = "bowel_movement"
TIMEZONE = "timezone"


class DestinyMiddleware(BaseMiddleware):
    def __init__(self, storage):
        self.storage = storage

    async def __call__(self, handler, event, data):
        destiny = None

        message = event.message
        callback_query = event.callback_query
        if message:
            if message.text == BowelMovementMessageCommand.START_BOWEL_MOVEMENT.value:
                destiny = BOWEL_MOVEMENT


        elif callback_query and callback_query.data:
            if any(
                    callback_query.data.startswith(prefix)
                    for prefix in (
                            BowelMovementCallbackKey.STOOL_CONSISTENCY,
                            BowelMovementCallbackKey.STOOL_BLOOD,
                            BowelMovementCallbackKey.STOOL_MUCUS,
                            BowelMovementCallbackKey.DELETE,
                    )
            ):
                destiny = BOWEL_MOVEMENT
            elif callback_query.data in (
                    BowelMovementCallbackKey.SKIP_NOTES,
                    BowelMovementCallbackKey.BACK_FROM_NOTES,
                    BowelMovementCallbackKey.BACK_FROM_MUCUS,
                    BowelMovementCallbackKey.BACK_FROM_BLOOD,
            ):
                destiny = BOWEL_MOVEMENT
            elif callback_query.data.startswith(MainCallbackKey.SET_HOUR_TIMEZONE):
                destiny = TIMEZONE
            elif callback_query.data.startswith(MainCallbackKey.SET_MINUTE_TIMEZONE):
                destiny = TIMEZONE
            elif callback_query.data == MainCallbackKey.SETTINGS_TIMEZONE:
                destiny = TIMEZONE

        if destiny is None and message:
            key = StorageKey(
                bot_id=message.bot.id,
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                destiny=BOWEL_MOVEMENT,
            )
            state = await self.storage.get_state(key)
            if state == BowelMovementStates.waiting_for_notes.state:
                destiny = BOWEL_MOVEMENT

        if destiny:
            data["destiny"] = destiny

        return await handler(event, data)
