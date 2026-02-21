"""Integration tests for bowel movement handlers"""
from unittest.mock import Mock, patch

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


class TestBowelMovementHandlers:
    """Integration tests for bowel movement handlers"""

    @pytest.mark.asyncio
    async def test_start_bowel_movement_recording_new(self, mock_message, mock_fsm_context, mock_async_session):
        """Test starting new bowel movement recording"""
        # Arrange
        mock_message.text = BowelMovementMessageCommand.START_BOWEL_MOVEMENT
        mock_message.from_user.id = 123
        mock_fsm_context.get_state.return_value = None

        mock_bowel_movement = Mock(spec=BowelMovement)
        mock_bowel_movement.id = 1

        with patch('bot.handlers.bowel_movement.BowelMovementService.create_bowel_movement') as mock_create:
            mock_create.return_value = mock_bowel_movement

            # Act
            await start_bowel_movement_recording(mock_message, mock_fsm_context, mock_async_session)

            # Assert
            mock_fsm_context.get_state.assert_called_once()
            mock_create.assert_called_once_with(mock_async_session, 123)
            mock_fsm_context.update_data.assert_called_once()
            mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.stool_consistency)

    @pytest.mark.asyncio
    async def test_start_bowel_movement_recording_already_in_progress(self, mock_message, mock_fsm_context,
                                                                      mock_async_session):
        """Test starting recording when another is already in progress"""
        # Arrange
        mock_message.text = BowelMovementMessageCommand.START_BOWEL_MOVEMENT
        mock_fsm_context.get_state.return_value = BowelMovementStates.stool_consistency.state

        # Act
        await start_bowel_movement_recording(mock_message, mock_fsm_context, mock_async_session)

        # Assert
        mock_fsm_context.get_state.assert_called_once()
        mock_message.answer.assert_called_once_with(text="Пожалуйста, завершите предыдущую запись")
        # Should not create new bowel movement
        mock_fsm_context.set_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_stool_consistency(self, mock_callback_query, mock_fsm_context, mock_async_session):
        """Test adding stool consistency information"""
        # Arrange
        mock_callback_query.data = f"{BowelMovementCallbackKey.STOOL_CONSISTENCY}:2"
        mock_fsm_context.get_data.return_value = {'bowel_movement_id': 1}

        with patch('bot.handlers.bowel_movement.BowelMovementService.update_bowel_movement') as mock_update:
            mock_update.return_value = None

            # Act
            await add_stool_consistency(mock_callback_query, mock_fsm_context, mock_async_session)

            # Assert
            mock_fsm_context.get_data.assert_called_once()
            mock_update.assert_called_once_with(
                session=mock_async_session,
                bowel_movement_id=1,
                stool_consistency=2
            )
            mock_callback_query.message.edit_text.assert_called_once()
            mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.mucus)

    @pytest.mark.asyncio
    async def test_add_stool_mucus(self, mock_callback_query, mock_fsm_context, mock_async_session):
        """Test adding mucus information"""
        # Arrange
        mock_callback_query.data = f"{BowelMovementCallbackKey.STOOL_MUCUS}:1"
        mock_fsm_context.get_data.return_value = {'bowel_movement_id': 1}

        with patch('bot.handlers.bowel_movement.BowelMovementService.update_bowel_movement') as mock_update:
            mock_update.return_value = None

            # Act
            await add_stool_mucus(mock_callback_query, mock_fsm_context, mock_async_session)

            # Assert
            mock_fsm_context.get_data.assert_called_once()
            mock_update.assert_called_once_with(
                session=mock_async_session,
                bowel_movement_id=1,
                mucus=1
            )
            mock_callback_query.message.edit_text.assert_called_once()
            mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.blood)

    @pytest.mark.asyncio
    async def test_add_stool_blood(self, mock_callback_query, mock_fsm_context, mock_async_session):
        """Test adding blood level information"""
        # Arrange
        mock_callback_query.data = f"{BowelMovementCallbackKey.STOOL_BLOOD}:0"
        mock_fsm_context.get_data.return_value = {'bowel_movement_id': 1}

        with patch('bot.handlers.bowel_movement.BowelMovementService.update_bowel_movement') as mock_update:
            mock_update.return_value = None

            # Act
            await add_stool_blood(mock_callback_query, mock_fsm_context, mock_async_session)

            # Assert
            mock_fsm_context.get_data.assert_called_once()
            mock_update.assert_called_once_with(
                session=mock_async_session,
                bowel_movement_id=1,
                blood_lvl=0
            )
            mock_callback_query.message.edit_text.assert_called_once()
            mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.waiting_for_notes)

    @pytest.mark.asyncio
    async def test_save_notes(self, mock_message, mock_fsm_context, mock_async_session):
        """Test saving notes for bowel movement"""
        # Arrange
        mock_message.text = "Some notes here"
        mock_fsm_context.get_data.return_value = {
            'bowel_movement_id': 1,
            'bowel_movement_msg_id': 123,
            'chat_id': 456
        }

        mock_bowel_movement = Mock(spec=BowelMovement)
        mock_bowel_movement.stool_consistency = 2  # MUSHY
        mock_bowel_movement.blood_lvl = 0
        mock_bowel_movement.mucus = 1
        mock_user = Mock(spec=User)
        mock_user.timezone_offset = 180

        with patch('bot.handlers.bowel_movement.BowelMovementService.update_bowel_movement') as mock_update:
            mock_update.return_value = mock_bowel_movement
            with patch('bot.handlers.bowel_movement.UserService.get_or_create_user') as mock_get_user:
                mock_get_user.return_value = mock_user
                with patch('bot.handlers.bowel_movement.get_result_msg_text') as mock_get_result:
                    mock_get_result.return_value = "Formatted result text"

                    # Act
                    await save_notes(mock_message, mock_fsm_context, mock_async_session)

                    # Assert
                    mock_fsm_context.get_data.assert_called_once()
                    mock_update.assert_called_once_with(
                        session=mock_async_session,
                        bowel_movement_id=1,
                        notes="Some notes here"
                    )
                    mock_get_user.assert_called_once_with(mock_async_session, mock_message.from_user.id)
                    mock_get_result.assert_called_once_with(mock_bowel_movement, 180)
                    mock_fsm_context.clear.assert_called_once()
                    mock_message.bot.edit_message_text.assert_called_once_with(
                        text="Formatted result text",
                        message_id=123,
                        reply_markup=None,
                        chat_id=456
                    )
                    mock_message.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_skip_notes(self, mock_callback_query, mock_fsm_context, mock_async_session):
        """Test skipping notes for bowel movement"""
        # Arrange
        mock_callback_query.data = BowelMovementCallbackKey.SKIP_NOTES.value
        mock_fsm_context.get_data.return_value = {'bowel_movement_id': 1}

        mock_bowel_movement = Mock(spec=BowelMovement)
        mock_bowel_movement.stool_consistency = 2  # MUSHY
        mock_bowel_movement.blood_lvl = 0
        mock_bowel_movement.mucus = 1
        mock_user = Mock(spec=User)
        mock_user.timezone_offset = 180

        with patch('bot.handlers.bowel_movement.BowelMovementService.get_bowel_movement_by_id') as mock_get:
            mock_get.return_value = mock_bowel_movement
            with patch('bot.handlers.bowel_movement.UserService.get_or_create_user') as mock_get_user:
                mock_get_user.return_value = mock_user
                with patch('bot.handlers.bowel_movement.get_result_msg_text') as mock_get_result:
                    mock_get_result.return_value = "Formatted result text"

                    # Act
                    await skip_notes(mock_callback_query, mock_fsm_context, mock_async_session)

                    # Assert
                    mock_fsm_context.get_data.assert_called_once()
                    mock_get.assert_called_once_with(
                        bowel_movement_id=1,
                        session=mock_async_session
                    )
                    mock_get_user.assert_called_once_with(mock_async_session, mock_callback_query.from_user.id)
                    mock_get_result.assert_called_once_with(mock_bowel_movement, 180)
                    mock_callback_query.message.edit_text.assert_called_once_with(
                        text="Formatted result text",
                        reply_markup=None
                    )
                    mock_fsm_context.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_back_from_mucus_to_stool_consistency(self, mock_callback_query, mock_fsm_context):
        """Test navigating back from mucus state to stool consistency state"""
        # Arrange
        with patch('bot.handlers.bowel_movement.get_bowel_movement_text') as mock_get_text, \
                patch('bot.handlers.bowel_movement.get_bowel_movement_keyboard') as mock_get_keyboard:
            mock_get_text.return_value = "Stool consistency text"
            mock_get_keyboard.return_value = "Stool consistency keyboard"

            # Act
            await back_from_mucus_to_stool_consistency(mock_callback_query, mock_fsm_context)

            # Assert
            mock_callback_query.message.edit_text.assert_called_once_with(
                text="Stool consistency text",
                reply_markup="Stool consistency keyboard"
            )
            mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.stool_consistency)

    @pytest.mark.asyncio
    async def test_back_from_blood_to_mucus_state(self, mock_callback_query, mock_fsm_context):
        """Test navigating back from blood state to mucus state"""
        # Arrange
        with patch('bot.handlers.bowel_movement.get_mucus_msg_text') as mock_get_text, \
                patch('bot.handlers.bowel_movement.get_mucus_msg_keyboard') as mock_get_keyboard:
            mock_get_text.return_value = "Mucus text"
            mock_get_keyboard.return_value = "Mucus keyboard"

            # Act
            await back_from_blood_to_mucus_state(mock_callback_query, mock_fsm_context)

            # Assert
            mock_callback_query.message.edit_text.assert_called_once_with(
                text="Mucus text",
                reply_markup="Mucus keyboard"
            )
            mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.mucus)

    @pytest.mark.asyncio
    async def test_back_from_notes_to_blood_record(self, mock_callback_query, mock_fsm_context):
        """Test navigating back from notes state to blood state"""
        # Arrange
        with patch('bot.handlers.bowel_movement.get_blood_msg_text') as mock_get_text, \
                patch('bot.handlers.bowel_movement.get_blood_msg_keyboard') as mock_get_keyboard:
            mock_get_text.return_value = "Blood text"
            mock_get_keyboard.return_value = "Blood keyboard"

            # Act
            await back_from_notes_to_blood_record(mock_callback_query, mock_fsm_context)

            # Assert
            mock_callback_query.message.edit_text.assert_called_once_with(
                text="Blood text",
                reply_markup="Blood keyboard"
            )
            mock_fsm_context.set_state.assert_called_once_with(BowelMovementStates.blood)


if __name__ == "__main__":
    pytest.main([__file__])
