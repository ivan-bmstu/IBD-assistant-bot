"""Pytest configuration and fixtures"""
import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_async_session():
    """Create a mock AsyncSession for database tests"""
    session = AsyncMock()
    # Configure common methods
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_fsm_context():
    """Create a mock FSMContext for aiogram handler tests"""
    context = AsyncMock()
    context.set_state = AsyncMock()
    context.get_state = AsyncMock()
    context.get_data = AsyncMock()
    context.update_data = AsyncMock()
    context.clear = AsyncMock()
    return context


@pytest.fixture
def mock_message():
    """Create a mock Message object for aiogram handler tests"""
    message = AsyncMock()
    message.message_id = 123
    message.chat = AsyncMock(id=456)
    message.from_user = AsyncMock(id=789)
    message.text = "/start"
    message.answer = AsyncMock()
    message.delete = AsyncMock()
    return message


@pytest.fixture
def mock_callback_query():
    """Create a mock CallbackQuery object for aiogram handler tests"""
    callback = AsyncMock()
    callback.message = AsyncMock()
    callback.message.message_id = 123
    callback.message.chat = AsyncMock(id=456)
    callback.message.edit_text = AsyncMock()
    callback.from_user = AsyncMock(id=789)
    callback.data = "test_callback_data"
    callback.answer = AsyncMock()
    return callback


# Enable asyncio for all tests
def pytest_collection_modifyitems(items):
    """Add asyncio marker to all async tests"""
    for item in items:
        if hasattr(item, 'fixturenames') and 'event_loop' in item.fixturenames:
            item.add_marker(pytest.mark.asyncio)
