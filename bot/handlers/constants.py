from enum import StrEnum


class BowelMovementMessageCommand(StrEnum):
    """Message commands for bowel movement handler"""
    START_BOWEL_MOVEMENT = '📝 Сделать запись'


class BowelMovementCallbackKey(StrEnum):
    """Callback keys for bowel movement handler"""
    SKIP = 'skip'
    FALSE_URGE = 'false_urge'
    GO_TO_STOOL_CONSISTENCY = 'go_to_stool_consistency'
    DELETE_CONFIRMATION = 'delete_confirmation'
    DELETE_RECORD = 'delete_record'
    SKIP_NOTES = 'skip_notes'
    STOOL_CONSISTENCY = 'stool_consistency'
    STOOL_BLOOD = 'stool_blood'
    STOOL_MUCUS = 'stool_mucus'
    BACK_FROM_STOOL_CONSISTENCY = 'back_from_stool_consistency'
    BACK_FROM_NOTES = 'back_from_notes'
    BACK_FROM_MUCUS = 'back_from_mucus'
    BACK_FROM_BLOOD = 'back_from_blood'
    BACK_FROM_DELETE_CONFIRMATION = 'back_from_delete_confirmation'


class BackFromDeleteBowelMovementToPosition(StrEnum):
    """Back from delete bowel movement to position"""
    INIT_STEP = 'init_step'
    FINAL_STEP = 'final_step'


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