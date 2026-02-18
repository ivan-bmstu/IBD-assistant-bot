from datetime import timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers.constants import BowelMovementCallbackKey
from database.models import BowelMovement
from database.models.bowel_movement import StoolConsistency, StoolBlood, Mucus


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
        for consistency_value, button_text in consistency_options[i:i + 2]:
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
        ),
    ])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_mucus_msg_text() -> str:
    return "Укажите, присутствует ли слизь в стуле"


def get_mucus_msg_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=Mucus.PRESENT.label,
                    callback_data=f'{BowelMovementCallbackKey.STOOL_MUCUS}:{Mucus.PRESENT.value}'
                )
            ],
            [
                InlineKeyboardButton(
                    text=Mucus.NOT_PRESENT.label,
                    callback_data=f'{BowelMovementCallbackKey.STOOL_MUCUS}:{Mucus.NOT_PRESENT.value}'
                )
            ],
            [
                InlineKeyboardButton(
                    text="Пропустить",
                    callback_data=f'{BowelMovementCallbackKey.STOOL_MUCUS}:{BowelMovementCallbackKey.SKIP}'
                )
            ],
            [
                InlineKeyboardButton(
                    text="Вернуться назад ⬅️",
                    callback_data=f'{BowelMovementCallbackKey.BACK_FROM_MUCUS}'
                )
            ],
        ]
    )



def get_blood_msg_text() -> str:
    return "Укажите количество крови в стуле"


def get_blood_msg_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{StoolBlood.TRACE.label}",
                    callback_data=f"{BowelMovementCallbackKey.STOOL_BLOOD}:{StoolBlood.TRACE.value}",
                ),
                InlineKeyboardButton(
                    text=f"{StoolBlood.MILD.label}",
                    callback_data=f"{BowelMovementCallbackKey.STOOL_BLOOD}:{StoolBlood.MILD.value}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{StoolBlood.MODERATE.label}",
                    callback_data=f"{BowelMovementCallbackKey.STOOL_BLOOD}:{StoolBlood.MODERATE.value}",
                ),
                InlineKeyboardButton(
                    text=f"{StoolBlood.SEVERE.label}",
                    callback_data=f"{BowelMovementCallbackKey.STOOL_BLOOD}:{StoolBlood.SEVERE.value}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Пропустить",
                    callback_data=f"{BowelMovementCallbackKey.STOOL_BLOOD}:{BowelMovementCallbackKey.SKIP}",
                ),
                InlineKeyboardButton(
                    text=f"{StoolBlood.NOT_PRESENT.label}",
                    callback_data=f"{BowelMovementCallbackKey.STOOL_BLOOD}:{StoolBlood.NOT_PRESENT.value}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Вернуться назад ⬅️",
                    callback_data=f"{BowelMovementCallbackKey.BACK_FROM_BLOOD}",
                ),
            ]
        ]
    )


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
    blood_lvl = (StoolBlood(bowel_movement.blood_lvl) if bowel_movement.blood_lvl is not None else None)
    mucus_lvl = Mucus(bowel_movement.mucus) if bowel_movement.mucus is not None else None

    offset_minutes = timezone_offset or 0
    local_dt = bowel_movement.created_at + timedelta(minutes=offset_minutes)

    notes = f"Примечания: {bowel_movement.notes}" if bowel_movement.notes else ""
    consistency_text = stool_consistency.label if stool_consistency else "—"
    blood_lvl_text = blood_lvl.label if blood_lvl is not None else "—"
    mucus_lvl_text = mucus_lvl.label if mucus_lvl is not None else "—"

    return (
        "📝 <b>Запись произведена успешно</b>\n\n"
        f"Дата: {local_dt.strftime('%d.%m.%Y')}\n"
        f"Время: {local_dt.strftime('%H:%M')}\n"
        f"Состояние стула: {consistency_text}\n"
        f"Слизь в стуле: {mucus_lvl_text}\n"
        f"Кровь в стуле: {blood_lvl_text}\n\n"
        f"{notes}"
    )
