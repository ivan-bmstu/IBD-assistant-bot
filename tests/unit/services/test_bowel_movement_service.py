"""Unit tests for BowelMovementService"""
import pytest
import unittest
from unittest.mock import AsyncMock, Mock

from service.bowel_movement import BowelMovementService
from bot.handlers.constants import BowelMovementCallbackKey


class TestBowelMovementService:
    """Test cases for BowelMovementService"""

    def test_parse_optional_int_valid_number(self):
        """Test parsing valid integer from callback data"""
        # Arrange
        callback_data = f"{BowelMovementCallbackKey.STOOL_CONSISTENCY}:42"

        # Act
        result = BowelMovementService.parse_optional_int(callback_data)

        # Assert
        assert result == 42

    def test_parse_optional_int_skip_value(self):
        """Test parsing skip value from callback data"""
        # Arrange
        callback_data = f"{BowelMovementCallbackKey.STOOL_CONSISTENCY}:{BowelMovementCallbackKey.SKIP}"

        # Act
        result = BowelMovementService.parse_optional_int(callback_data)

        # Assert
        assert result is None

    def test_parse_optional_int_invalid_number(self):
        """Test parsing invalid integer raises ValueError"""
        # Arrange
        callback_data = f"{BowelMovementCallbackKey.STOOL_CONSISTENCY}:not_a_number"

        # Act & Assert
        with pytest.raises(ValueError):
            BowelMovementService.parse_optional_int(callback_data)

    def test_parse_optional_int_empty_after_colon(self):
        """Test parsing empty string after colon raises ValueError"""
        # Arrange
        callback_data = f"{BowelMovementCallbackKey.STOOL_CONSISTENCY}:"

        # Act & Assert
        with pytest.raises(ValueError):
            BowelMovementService.parse_optional_int(callback_data)

    def test_parse_optional_int_no_colon(self):
        """Test parsing string without colon raises IndexError"""
        # Arrange
        callback_data = "no_colon_here"

        # Act & Assert
        with pytest.raises(IndexError):
            BowelMovementService.parse_optional_int(callback_data)

    @pytest.mark.asyncio
    async def test_create_bowel_movement(self, mock_async_session):
        """Test creating bowel movement with mocked repository"""
        # Arrange
        mock_repository_return = Mock()
        mock_repository_return.id = 1

        # Mock the repository method
        with unittest.mock.patch('service.bowel_movement.BowelMovementRepository.create_bowel_movement') as mock_create:
            mock_create.return_value = mock_repository_return

            # Act
            result = await BowelMovementService.create_bowel_movement(
                session=mock_async_session,
                user_id=123
            )

            # Assert
            mock_create.assert_called_once_with(
                session=mock_async_session,
                user_id=123,
                movement_date=None,
                movement_time=None,
                notes=None,
                stool_consistency=None
            )
            assert result == mock_repository_return

    @pytest.mark.asyncio
    async def test_update_bowel_movement(self, mock_async_session):
        """Test updating bowel movement with mocked repository"""
        # Arrange
        mock_repository_return = Mock()

        with unittest.mock.patch('service.bowel_movement.BowelMovementRepository.update_bowel_movement') as mock_update:
            mock_update.return_value = mock_repository_return

            # Act
            result = await BowelMovementService.update_bowel_movement(
                session=mock_async_session,
                bowel_movement_id=1,
                notes="Some notes",
                stool_consistency=2,
                blood_lvl=1,
                mucus=0
            )

            # Assert
            mock_update.assert_called_once_with(
                session=mock_async_session,
                movement_id=1,
                notes="Some notes",
                stool_consistency=2,
                blood_lvl=1,
                mucus=0
            )
            assert result == mock_repository_return

    @pytest.mark.asyncio
    async def test_get_bowel_movement_by_id(self, mock_async_session):
        """Test getting bowel movement by ID with mocked repository"""
        # Arrange
        mock_repository_return = Mock()

        with unittest.mock.patch('service.bowel_movement.BowelMovementRepository.get_bowel_movement_by_id') as mock_get:
            mock_get.return_value = mock_repository_return

            # Act
            result = await BowelMovementService.get_bowel_movement_by_id(
                session=mock_async_session,
                bowel_movement_id=1
            )

            # Assert
            mock_get.assert_called_once_with(
                session=mock_async_session,
                id=1
            )
            assert result == mock_repository_return


if __name__ == "__main__":
    pytest.main([__file__])
