from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.constants import BowelMovementMessageCommand, BowelMovementCallbackKey
from bot.keyboards.bowel_movement import get_bowel_movement_keyboard, get_skip_notes_keyboard, get_result_msg_text, \
    get_bowel_movement_text
from database.models import User
from database.models.bowel_movement import BowelMovement
from service.bowel_movement import BowelMovementService
from service.user import UserService

router = Router()


class BowelMovementStates(StatesGroup):
    """FSM states for bowel movement recording"""
    stool_consistency = State()
    waiting_for_notes = State()


class BowelMovementStateData(BaseModel):
    bowel_movement_id: int
    bowel_movement_msg_id: int
    chat_id: int


@router.message(F.text == BowelMovementMessageCommand.START_BOWEL_MOVEMENT)
async def start_bowel_movement_recording(message: Message, state: FSMContext, session: AsyncSession):
    """Start the bowel movement recording process"""
    current_state = await state.get_state()
    # Список всех состояний BowelMovementStates
    bowel_movement_states = [
        BowelMovementStates.stool_consistency.state,
        BowelMovementStates.waiting_for_notes.state
    ]
    if current_state in bowel_movement_states:
        await message.answer(text="Пожалуйста, завершите предыдущую запись")
        return
    bowel_movement: BowelMovement = await BowelMovementService.create_bowel_movement(session, message.from_user.id)
    sent_msg: Message = await message.answer(
        text=get_bowel_movement_text(),
        reply_markup=get_bowel_movement_keyboard()
    )
    await state.update_data(
        bowel_movement_id=bowel_movement.id,
        bowel_movement_msg_id=sent_msg.message_id,
        chat_id=sent_msg.chat.id
    )
    await state.set_state(BowelMovementStates.stool_consistency)


@router.message(BowelMovementStates.waiting_for_notes)
async def save_notes(message: Message, state: FSMContext, session: AsyncSession):
    """Save notes"""
    data = await state.get_data()
    bowel_movement_id = data["bowel_movement_id"]
    bot_msg_id = data["bowel_movement_msg_id"]
    chat_id = data["chat_id"]
    bowel_movement: BowelMovement = await BowelMovementService.update_bowel_movement(
        session=session,
        bowel_movement_id=bowel_movement_id,
        notes=message.text
    )
    user: User = await UserService.get_or_create_user(session, message.from_user.id)
    await state.clear()
    await message.bot.edit_message_text(
        text=get_result_msg_text(bowel_movement, user.timezone_offset),
        message_id=bot_msg_id,
        reply_markup=None,
        chat_id=chat_id
    )
    await message.delete()


@router.callback_query(F.data.startswith(BowelMovementCallbackKey.STOOL_CONSISTENCY))
async def add_stool_consistency(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Add information about stool consistency to the bowel movement"""
    stool_consistency_val: int | None = BowelMovementService.get_stool_consistency_data(callback.data)
    if stool_consistency_val is not None:
        state_data: BowelMovementStateData = await state.get_data()
        bowel_movement_id = state_data['bowel_movement_id']
        await BowelMovementService.update_bowel_movement(
            session=session,
            bowel_movement_id=bowel_movement_id,
            stool_consistency=stool_consistency_val,
        )
    await callback.message.edit_text(
        text="Если хотите оставить заметку, пришлите ее в сообщении\nИли пропустите этот шаг",
        reply_markup=get_skip_notes_keyboard()
    )
    await state.set_state(BowelMovementStates.waiting_for_notes)


@router.callback_query(F.data == BowelMovementCallbackKey.SKIP_NOTES.value)
async def skip_notes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """User skipped notes"""
    data = await state.get_data()
    bowel_movement_id: int = data["bowel_movement_id"]
    bowel_movement: BowelMovement = await BowelMovementService.get_bowel_movement_by_id(
        bowel_movement_id=bowel_movement_id,
        session=session,
    )
    user: User = await UserService.get_or_create_user(session, callback.from_user.id)
    await callback.message.edit_text(
        text=get_result_msg_text(bowel_movement, user.timezone_offset),
        reply_markup=None
    )
    await state.clear()


@router.callback_query(F.data.startswith(BowelMovementCallbackKey.BACK_FROM_NOTES))
async def back_from_notes(callback: CallbackQuery, state: FSMContext):
    """Back to the bowel movement recording process"""
    await callback.message.edit_text(
        text=get_bowel_movement_text(),
        reply_markup=get_bowel_movement_keyboard()
    )
    await state.set_state(BowelMovementStates.stool_consistency)
