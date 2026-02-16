from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.constants import BowelMovementMessageCommand, MainMessageCommand, MainCallbackKey
from bot.keyboards.main_keyboard import get_main_keyboard, get_timezone_hour_keyboard, get_timezone_minutes_keyboard, \
    get_settings_keyboard
from database.models import User
from service.user import UserService
from service.utills import format_timezone

router = Router()


class StartStates(StatesGroup):
    """FSM states for start command"""
    timezone_hour = State()
    timezone_minute = State()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext):
    """Handle /start command"""
    # Get or create user
    user = await UserService.get_or_create_user(
        session=session,
        telegram_id=message.from_user.id,
        language_code=message.from_user.language_code,
    )

    welcome_text = (
        "👋 Привет! Я бот-трекер для людей с болезнью Крона и язвенным колитом.\n\n"
        "Я помогу вам отслеживать походы в туалет и отслеживать состояние.\n\n"
    )
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

    user_timezone: int = user.timezone_offset
    if user_timezone is None:
        await state.set_state(StartStates.timezone_hour)
        await message.answer(
            text="Давайте для начала установим вашу таймзону\n\nУкажите часовой пояс, а затем минутное смещение",
            reply_markup=get_timezone_hour_keyboard()
        )


@router.callback_query(F.data.startswith(MainCallbackKey.SET_HOUR_TIMEZONE))
async def set_hour_timezone(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Set user hour timezone"""
    data_val: str = callback.data.split(':')[1]
    if data_val == MainCallbackKey.SKIP:
        timezone_offset = 0
    else:
        timezone_offset: int = int(data_val)
    await UserService.set_user_hour_timezone(session, callback.from_user.id, timezone_offset)
    await callback.message.edit_text(
        text="Укажите минуты таймзоны",
        reply_markup=get_timezone_minutes_keyboard()
    )
    await state.set_state(StartStates.timezone_minute)


@router.callback_query(F.data.startswith(MainCallbackKey.SET_MINUTE_TIMEZONE))
async def set_minute_timezone(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Set user minute timezone"""
    data_val: str = callback.data.split(':')[1]
    if data_val == MainCallbackKey.SKIP.value:
        timezone_offset = 0
    else:
        timezone_offset: int = int(data_val)
    user: User = await UserService.set_user_minute_timezone(session, callback.from_user.id, timezone_offset)
    timezone: str = format_timezone(user.timezone_offset)
    await callback.message.edit_text(
        text=f"Таймзона успешно установлена\n\nВаша текущая таймзона: {timezone}"
    )
    await state.clear()
    await callback.message.answer(
        f"Для записи данных используйте кнопку:\n• {BowelMovementMessageCommand.START_BOWEL_MOVEMENT.value} - для записи факта похода в туалет и заметок"
    )


@router.message(F.text == MainMessageCommand.USER_SETTINGS)
async def user_settings(message: Message, state: FSMContext, session: AsyncSession):
    """Show user settings"""
    user: User = await UserService.get_or_create_user(session, message.from_user.id)
    timezone: str = format_timezone(user.timezone_offset)
    await message.answer(
        text=f"Ваша текущая таймзона: {timezone}",
        reply_markup=get_settings_keyboard()
    )


@router.callback_query(F.data == MainCallbackKey.SETTINGS_TIMEZONE.value)
async def timezone_settings(callback: CallbackQuery, state: FSMContext):
    """Edit timezone settings"""
    await state.set_state(StartStates.timezone_hour)
    await callback.message.edit_text(
        text="Укажите часы таймзоны",
        reply_markup=get_timezone_hour_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = (
        "📚 <b>Справка по командам бота:</b>\n\n"
        "<b>Основные команды:</b>\n"
        "/start - Начать работу с ботом\n"
        "/about - Информация о боте\n"
        "/help - Показать эту справку\n\n"
        "<b>Для записи данных используйте кнопку:</b>\n"
        f"• {BowelMovementMessageCommand.START_BOWEL_MOVEMENT.value} - для записи факта похода в туалет и заметок\n\n"
        "Все данные хранятся анонимно и используются только для вашего анализа."
    )
    await message.answer(help_text)


@router.message(F.text == MainMessageCommand.HELP.value)
async def msg_about(message: Message):
    await cmd_help(message)


@router.message(Command("about"))
async def cmd_about(message: Message):
    """Handle /about command"""
    about_text = (
        "ℹ️ <b>О боте:</b>\n\n"
        "Этот бот создан для помощи людям с воспалительными заболеваниями кишечника "
        "(болезнь Крона и язвенный колит).\n\n"
        "<b>Цели проекта:</b>\n"
        "1. Помочь отслеживать симптомы и триггеры\n"
        "2. Упростить ведение дневника для консультаций с врачом\n"
        "3. Предоставить аналитику для понимания динамики заболевания\n\n"
        "Бот не заменяет консультацию врача! Все решения о лечении должны приниматься "
        "под наблюдением специалиста.\n\n"
        "Для связи с разработчиком: laefree@yandex.ru"
    )
    await message.answer(about_text)


@router.message(F.text == MainMessageCommand.ABOUT)
async def msg_about(message: Message):
    await cmd_about(message)
