from datetime import timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers.constants import BowelMovementCallbackKey
from database.models import BowelMovement
from database.models.bowel_movement import StoolConsistency


def get_bowel_movement_text() -> str:
    return "📝 <b>Произвести запись</b>\n\nУкажите состояние стула:"


def get_bowel_movement_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for bowel movement input"""
    # Маппинг значений консистенции на текст кнопок
    consistency_options = [
        (StoolConsistency.LIQUID.value, 'Жидкий'),
        (StoolConsistency.MUSHY.value, 'Кашицеобразный'),
        (StoolConsistency.NORMAL.value, 'Нормальный'),
        (StoolConsistency.HARD.value, 'Твердый'),
    ]

    inline_keyboard = []

    # Создаем кнопки выбора консистенции (по 2 кнопки в строке)
    for i in range(0, len(consistency_options), 2):
        row: list[InlineKeyboardButton] = []
        for consistency_value, button_text in consistency_options[i:i+2]:
            row.append(
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f'{BowelMovementCallbackKey.STOOL_CONSISTENCY}:{consistency_value}'
                )
            )
        inline_keyboard.append(row)

    # Кнопка "Пропустить" отдельной строкой
    inline_keyboard.append([
        InlineKeyboardButton(
            text='Пропустить',
            callback_data=f'{BowelMovementCallbackKey.STOOL_CONSISTENCY}:{BowelMovementCallbackKey.SKIP}'
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_skip_notes_keyboard():
    """Get keyboard for skipping notes"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Вернуться назад ⬅️",
                    callback_data=f"{BowelMovementCallbackKey.BACK_FROM_NOTES}"
                ),
                InlineKeyboardButton(text="Пропустить", callback_data=BowelMovementCallbackKey.SKIP_NOTES),
            ]
        ]
    )


def get_result_msg_text(bowel_movement: BowelMovement, timezone_offset: int | None = 0) -> str:
    stool_consistency = (
        StoolConsistency(bowel_movement.stool_consistency)
        if bowel_movement.stool_consistency is not None
        else None
    )

    offset_minutes = timezone_offset or 0
    local_dt = bowel_movement.created_at + timedelta(minutes=offset_minutes)

    notes = f"Примечания: {bowel_movement.notes}" if bowel_movement.notes else ""
    consistency_text = stool_consistency.label if stool_consistency else "—"

    return (
        "📝 <b>Запись произведена успешно</b>\n\n"
        f"Дата: {local_dt.strftime('%d.%m.%Y')}\n"
        f"Время: {local_dt.strftime('%H:%M')}\n"
        f"Состояние стула: {consistency_text}\n"
        f"{notes}"
    )
