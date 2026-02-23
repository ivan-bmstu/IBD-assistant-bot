"""Integration tests for bowel movement handlers"""
from datetime import datetime
from unittest.mock import Mock, AsyncMock

import pytest

from bot.handlers.bowel_movement import (
    start_bowel_movement_recording,
    add_stool_consistency,
    add_stool_mucus,
    add_stool_blood,
    save_notes,
    skip_notes,
    BowelMovementStates,
    back_from_mucus_to_stool_consistency,
    back_from_blood_to_mucus_state,
    back_from_notes_to_blood_record,
)
from bot.handlers.constants import BowelMovementMessageCommand, BowelMovementCallbackKey
from database.models import User
from database.models.bowel_movement import BowelMovement
from service.bowel_movement import BowelMovementService
from service.user import UserService


@pytest.fixture
def mock_user_service():
    """Fixture for a mocked UserService."""
    service = Mock(spec=UserService)
    service.get_or_create_user = AsyncMock()
    return service


@pytest.fixture
def mock_bowel_movement_service():
    """Fixture for a mocked BowelMovementService."""
    service = Mock(spec=BowelMovementService)
    service.create_bowel_movement = AsyncMock()
    service.update_bowel_movement = AsyncMock()
    service.get_bowel_movement_by_id = AsyncMock()
    return service


class TestBowelMovementHandlers:
    """Integration tests for bowel movement handlers"""

    @pytest.mark.asyncio
    async def test_start_bowel_movement_recording_new(self, mock_message, mock_fsm_context, mock_async_session,
                                                      mock_bowel_movement_service):
        """Test starting new bowel movement recording"""
        # Arrange
        mock_message.text = BowelMovementMessageCommand.START_BOWEL_MOVEMENT
        mock_message.from_user.id = 123
        mock_fsm_context.get_state.return_value = None

        mock_bowel_movement = Mock(spec=BowelMovement)
        mock_bowel_movement.id = 1
        mock_bowel_movement_service.create_bowel_movement.return_value = mock_bowel_movement

        # Act
        await start_bowel_movement_recording(mock_message, mock_fsm_context, mock_async_session,
                                             mock_bowel_movement_service)

        # Assert
        mock_fsm_context.get_state.assert_called_once()
        mock_bowel_movement_service.create_bowel_movement.assert_called_once_with(mock_async_session, 123)
        mock_fsm_context.update_data.assert_called_once()
        mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.init_conditional)

    @pytest.mark.asyncio
    async def test_start_bowel_movement_recording_already_in_progress(self, mock_message, mock_fsm_context,
                                                                      mock_async_session,
                                                                      mock_bowel_movement_service):
        """Test starting recording when another is already in progress"""
        # Arrange
        mock_message.text = BowelMovementMessageCommand.START_BOWEL_MOVEMENT
        mock_fsm_context.get_state.return_value = BowelMovementStates.stool_consistency.state

        # Act
        await start_bowel_movement_recording(mock_message, mock_fsm_context, mock_async_session,
                                             mock_bowel_movement_service)

        # Assert
        mock_fsm_context.get_state.assert_called_once()
        mock_message.answer.assert_called_once_with(text="Пожалуйста, завершите предыдущую запись")
        mock_bowel_movement_service.create_bowel_movement.assert_not_called()
        mock_fsm_context.set_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_stool_consistency(self, mock_callback_query, mock_fsm_context, mock_async_session,
                                         mock_bowel_movement_service):
        """Test adding stool consistency information"""
        # Arrange
        mock_callback_query.data = f"{BowelMovementCallbackKey.STOOL_CONSISTENCY}:2"
        mock_fsm_context.get_data.return_value = {
            'bowel_movement_id': 1,
            'bowel_movement_msg_id': 123,
            'chat_id': 456
        }

        # Act
        await add_stool_consistency(mock_callback_query, mock_fsm_context, mock_async_session,
                                    mock_bowel_movement_service)

        # Assert
        mock_fsm_context.get_data.assert_called_once()
        mock_bowel_movement_service.update_bowel_movement.assert_called_once_with(
            session=mock_async_session,
            bowel_movement_id=1,
            stool_consistency=2
        )
        mock_callback_query.message.edit_text.assert_called_once()
        mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.mucus)

    @pytest.mark.asyncio
    async def test_add_stool_mucus(self, mock_callback_query, mock_fsm_context, mock_async_session,
                                   mock_bowel_movement_service):
        """Test adding mucus information"""
        # Arrange
        mock_callback_query.data = f"{BowelMovementCallbackKey.STOOL_MUCUS}:1"
        mock_fsm_context.get_data.return_value = {
            'bowel_movement_id': 1,
            'bowel_movement_msg_id': 123,
            'chat_id': 456
        }

        # Act
        await add_stool_mucus(mock_callback_query, mock_fsm_context, mock_async_session, mock_bowel_movement_service)

        # Assert
        mock_fsm_context.get_data.assert_called_once()
        mock_bowel_movement_service.update_bowel_movement.assert_called_once_with(
            session=mock_async_session,
            bowel_movement_id=1,
            mucus=1
        )
        mock_callback_query.message.edit_text.assert_called_once()
        mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.blood)

    @pytest.mark.asyncio
    async def test_add_stool_blood(self, mock_callback_query, mock_fsm_context, mock_async_session,
                                   mock_bowel_movement_service):
        """Test adding blood level information"""
        # Arrange
        mock_callback_query.data = f"{BowelMovementCallbackKey.STOOL_BLOOD}:0"
        mock_fsm_context.get_data.return_value = {
            'bowel_movement_id': 1,
            'bowel_movement_msg_id': 123,
            'chat_id': 456
        }

        # Act
        await add_stool_blood(mock_callback_query, mock_fsm_context, mock_async_session, mock_bowel_movement_service)

        # Assert
        mock_fsm_context.get_data.assert_called_once()
        mock_bowel_movement_service.update_bowel_movement.assert_called_once_with(
            session=mock_async_session,
            bowel_movement_id=1,
            blood_lvl=0
        )
        mock_callback_query.message.edit_text.assert_called_once()
        mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.waiting_for_notes)

    @pytest.mark.asyncio
    async def test_save_notes(self, mock_message, mock_fsm_context, mock_async_session, mock_user_service,
                              mock_bowel_movement_service):
        """Test saving notes for bowel movement"""
        # Arrange
        mock_message.text = "Some notes here"
        mock_fsm_context.get_data.return_value = {
            'bowel_movement_id': 1,
            'bowel_movement_msg_id': 123,
            'chat_id': 456
        }

        mock_bowel_movement = Mock(spec=BowelMovement)
        mock_bowel_movement.stool_consistency = 2
        mock_bowel_movement.blood_lvl = 0
        mock_bowel_movement.mucus = 1
        mock_bowel_movement.created_at = datetime.now()
        mock_user = Mock(spec=User)
        mock_user.timezone_offset = 180
        mock_bowel_movement_service.update_bowel_movement.return_value = mock_bowel_movement
        mock_user_service.get_or_create_user.return_value = mock_user

        # Act
        await save_notes(mock_message, mock_fsm_context, mock_async_session, mock_bowel_movement_service,
                         mock_user_service)

        # Assert
        mock_fsm_context.get_data.assert_called_once()
        mock_bowel_movement_service.update_bowel_movement.assert_called_once_with(
            session=mock_async_session,
            bowel_movement_id=1,
            notes="Some notes here"
        )
        mock_user_service.get_or_create_user.assert_called_once_with(mock_async_session, mock_message.from_user.id)
        mock_fsm_context.clear.assert_called_once()
        mock_message.bot.edit_message_text.assert_called_once()
        mock_message.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_skip_notes(self, mock_callback_query, mock_fsm_context, mock_async_session, mock_user_service,
                              mock_bowel_movement_service):
        """Test skipping notes for bowel movement"""
        # Arrange
        mock_callback_query.data = BowelMovementCallbackKey.SKIP_NOTES.value
        mock_fsm_context.get_data.return_value = {
            'bowel_movement_id': 1,
            'bowel_movement_msg_id': 123,
            'chat_id': 456
        }

        mock_bowel_movement = Mock(spec=BowelMovement)
        mock_bowel_movement.stool_consistency = 3
        mock_bowel_movement.blood_lvl = 1
        mock_bowel_movement.mucus = 0
        mock_bowel_movement.created_at = datetime.now()
        mock_user = Mock(spec=User)
        mock_user.timezone_offset = 180
        mock_bowel_movement_service.get_bowel_movement_by_id.return_value = mock_bowel_movement
        mock_user_service.get_or_create_user.return_value = mock_user

        # Act
        await skip_notes(mock_callback_query, mock_fsm_context, mock_async_session, mock_bowel_movement_service,
                         mock_user_service)

        # Assert
        mock_fsm_context.get_data.assert_called_once()
        mock_bowel_movement_service.get_bowel_movement_by_id.assert_called_once_with(
            bowel_movement_id=1,
            session=mock_async_session
        )
        mock_user_service.get_or_create_user.assert_called_once_with(mock_async_session,
                                                                      mock_callback_query.from_user.id)
        mock_callback_query.message.edit_text.assert_called_once()
        mock_fsm_context.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_back_from_mucus_to_stool_consistency(self, mock_callback_query, mock_fsm_context):
        """Test navigating back from mucus state to stool consistency state"""
        mock_fsm_context.get_data.return_value = {
            'bowel_movement_id': 1,
            'bowel_movement_msg_id': 123,
            'chat_id': 456
        }
        await back_from_mucus_to_stool_consistency(mock_callback_query, mock_fsm_context)
        mock_callback_query.message.edit_text.assert_called_once()
        mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.stool_consistency)

    @pytest.mark.asyncio
    async def test_back_from_blood_to_mucus_state(self, mock_callback_query, mock_fsm_context):
        """Test navigating back from blood state to mucus state"""
        await back_from_blood_to_mucus_state(mock_callback_query, mock_fsm_context)
        mock_callback_query.message.edit_text.assert_called_once()
        mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.mucus)

    @pytest.mark.asyncio
    async def test_back_from_notes_to_blood_record(self, mock_callback_query, mock_fsm_context):
        """Test navigating back from notes state to blood state"""
        await back_from_notes_to_blood_record(mock_callback_query, mock_fsm_context)
        mock_callback_query.message.edit_text.assert_called_once()
        mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.blood)


if __name__ == "__main__":
    pytest.main([__file__])
