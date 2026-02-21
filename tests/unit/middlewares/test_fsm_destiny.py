"""Unit tests for DestinyMiddleware"""
from unittest.mock import AsyncMock, Mock

import pytest

from bot.handlers.constants import MainCallbackKey, BowelMovementMessageCommand
from bot.middlewares.fsm_destiny import DestinyMiddleware, BOWEL_MOVEMENT, TIMEZONE
from bot.handlers.bowel_movement import BowelMovementStates


@pytest.fixture
def mock_storage():
    """Fixture for a mocked FSM storage."""
    storage = AsyncMock()
    # Default behavior: no state found
    storage.get_state.return_value = None
    return storage


@pytest.fixture
def mock_handler():
    """Fixture for a mocked handler."""
    return AsyncMock()


class TestDestinyMiddleware:
    """Test cases for the DestinyMiddleware."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("message_text, expected_destiny", [
        (BowelMovementMessageCommand.START_BOWEL_MOVEMENT.value, BOWEL_MOVEMENT),
        ("some random text", None),
        (None, None),
    ])
    async def test_message_destiny(self, mock_storage, mock_handler, message_text, expected_destiny):
        """
        Tests that destiny is correctly identified from message text.
        """
        # Arrange
        middleware = DestinyMiddleware(mock_storage)
        mock_message = Mock()
        mock_message.text = message_text
        # Mock bot and user IDs needed for StorageKey creation
        mock_message.bot.id = 123
        mock_message.chat.id = 456
        mock_message.from_user.id = 789

        event = Mock(message=mock_message, callback_query=None)
        data = {}

        # Act
        await middleware(handler=mock_handler, event=event, data=data)

        # Assert
        # The handler should always be called
        mock_handler.assert_called_once_with(event, data)
        # Check if destiny was added to data correctly
        if expected_destiny:
            assert "destiny" in data
            assert data["destiny"] == expected_destiny
        else:
            assert "destiny" not in data

    @pytest.mark.asyncio
    @pytest.mark.parametrize("callback_data, expected_destiny", [
        (MainCallbackKey.SET_HOUR_TIMEZONE, TIMEZONE),
        ("something_else", None),
        (None, None),
    ])
    async def test_callback_destiny(self, mock_storage, mock_handler, callback_data, expected_destiny):
        """
        Tests that destiny is correctly identified from callback data.
        """
        # Arrange
        middleware = DestinyMiddleware(mock_storage)
        mock_callback = Mock()
        mock_callback.data = callback_data
        event = Mock(message=None, callback_query=mock_callback)
        data = {}

        # Act
        await middleware(handler=mock_handler, event=event, data=data)

        # Assert
        # The handler should always be called
        mock_handler.assert_called_once_with(event, data)
        # Check if destiny was added to data correctly
        if expected_destiny:
            assert "destiny" in data
            assert data["destiny"] == expected_destiny
        else:
            assert "destiny" not in data

    @pytest.mark.asyncio
    async def test_destiny_for_notes_state(self, mock_storage, mock_handler):
        """
        Tests that destiny is correctly identified for a user in the 'waiting_for_notes' state.
        """
        # Arrange
        middleware = DestinyMiddleware(mock_storage)
        # Simulate that the user is in the waiting_for_notes state
        mock_storage.get_state.return_value = BowelMovementStates.waiting_for_notes.state
        mock_message = Mock()
        mock_message.text = "This is my note"
        mock_message.bot.id = 123
        mock_message.chat.id = 456
        mock_message.from_user.id = 789
        event = Mock(message=mock_message, callback_query=None)
        data = {}

        # Act
        await middleware(handler=mock_handler, event=event, data=data)

        # Assert
        mock_handler.assert_called_once_with(event, data)
        assert "destiny" in data
        assert data["destiny"] == BOWEL_MOVEMENT
        mock_storage.get_state.assert_called_once()
