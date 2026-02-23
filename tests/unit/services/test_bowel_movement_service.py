"""Unit tests for BowelMovementService"""
import pytest
from unittest.mock import AsyncMock, Mock

from database.repository.bowel_movements import BowelMovementRepository
from service.bowel_movement import BowelMovementService
from bot.handlers.constants import BowelMovementCallbackKey


@pytest.fixture
def mock_bowel_movement_repo():
    """Fixture for a mocked BowelMovementRepository."""
    repo = Mock(spec=BowelMovementRepository)
    repo.create_bowel_movement = AsyncMock()
    repo.update_bowel_movement = AsyncMock()
    repo.get_bowel_movement_by_id = AsyncMock()
    return repo


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

    @pytest.mark.skip("Is it better raise ValueError or return None?")
    def test_parse_optional_int_invalid_number(self):
        """Test parsing invalid integer raises ValueError"""
        # Arrange
        callback_data = f"{BowelMovementCallbackKey.STOOL_CONSISTENCY}:not_a_number"

        # Act & Assert
        with pytest.raises(ValueError):
            BowelMovementService.parse_optional_int(callback_data)

    @pytest.mark.skip("Is it better raise ValueError or return None?")
    def test_parse_optional_int_empty_after_colon(self):
        """Test parsing empty string after colon raises ValueError"""
        # Arrange
        callback_data = f"{BowelMovementCallbackKey.STOOL_CONSISTENCY}:"

        # Act & Assert
        with pytest.raises(ValueError):
            BowelMovementService.parse_optional_int(callback_data)

    @pytest.mark.skip("Is it better raise IndexError or return None?")
    def test_parse_optional_int_no_colon(self):
        """Test parsing string without colon raises IndexError"""
        # Arrange
        callback_data = "no_colon_here"

        # Act & Assert
        with pytest.raises(IndexError):
            BowelMovementService.parse_optional_int(callback_data)

    @pytest.mark.asyncio
    async def test_create_bowel_movement(self, mock_async_session, mock_bowel_movement_repo):
        """Test creating bowel movement delegates to the repository"""
        # Arrange
        service = BowelMovementService(bowel_movement_repository=mock_bowel_movement_repo)
        mock_bowel_movement = Mock()
        mock_bowel_movement_repo.create_bowel_movement.return_value = mock_bowel_movement

        # Act
        result = await service.create_bowel_movement(
            session=mock_async_session,
            user_id=123
        )

        # Assert
        mock_bowel_movement_repo.create_bowel_movement.assert_called_once_with(
            session=mock_async_session,
            user_id=123,
            movement_date=None,
            movement_time=None,
            notes=None,
            stool_consistency=None
        )
        assert result == mock_bowel_movement

    @pytest.mark.asyncio
    async def test_update_bowel_movement(self, mock_async_session, mock_bowel_movement_repo):
        """Test updating bowel movement delegates to the repository"""
        # Arrange
        service = BowelMovementService(bowel_movement_repository=mock_bowel_movement_repo)
        mock_bowel_movement = Mock()
        mock_bowel_movement_repo.update_bowel_movement.return_value = mock_bowel_movement

        # Act
        result = await service.update_bowel_movement(
            session=mock_async_session,
            bowel_movement_id=1,
            notes="Some notes",
            stool_consistency=2,
            blood_lvl=1,
            mucus=0,
            is_false_urge=False,
            user_id=1,
        )

        # Assert
        mock_bowel_movement_repo.update_bowel_movement.assert_called_once_with(
            session=mock_async_session,
            movement_id=1,
            notes="Some notes",
            stool_consistency=2,
            blood_lvl=1,
            mucus=0,
            is_false_urge=False,
            user_id=1
        )
        assert result == mock_bowel_movement

    @pytest.mark.asyncio
    async def test_get_bowel_movement_by_id(self, mock_async_session, mock_bowel_movement_repo):
        """Test getting bowel movement by ID delegates to the repository"""
        # Arrange
        service = BowelMovementService(bowel_movement_repository=mock_bowel_movement_repo)
        mock_bowel_movement = Mock()
        mock_bowel_movement_repo.get_bowel_movement_by_id.return_value = mock_bowel_movement

        # Act
        result = await service.get_bowel_movement_by_id(
            session=mock_async_session,
            bowel_movement_id=1,
            user_id=1,
        )

        # Assert
        mock_bowel_movement_repo.get_bowel_movement_by_id.assert_called_once_with(
            session=mock_async_session,
            bowel_movement_id=1,
            user_id=1,
        )
        assert result == mock_bowel_movement


if __name__ == "__main__":
    pytest.main([__file__])
