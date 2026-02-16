from enum import StrEnum


class BowelMovementMessageCommand(StrEnum):
    """Message commands for bowel movement handler"""
    START_BOWEL_MOVEMENT = '📝 Сделать запись'


class BowelMovementCallbackKey(StrEnum):
    """Callback keys for bowel movement handler"""
    SKIP = 'skip'
    SKIP_NOTES = 'skip_notes'
    STOOL_CONSISTENCY = 'stool_consistency'
    BACK_FROM_NOTES = 'back_from_notes'


class MainMessageCommand(StrEnum):
    """Message commands for start handler"""
    USER_SETTINGS = '⚙️ Настройки'
    HELP = '❓ Помощь'
    ABOUT = 'ℹ️ О боте'


class MainCallbackKey(StrEnum):
    """Callback keys for start handler"""
    SETTINGS_TIMEZONE = "settings_timezone"
    SET_HOUR_TIMEZONE = "set_hour_timezone"
    SET_MINUTE_TIMEZONE = "set_minute_timezone"
    SKIP = "skip"