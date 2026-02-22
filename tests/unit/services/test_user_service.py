"""Unit tests for UserService"""
from unittest.mock import AsyncMock, Mock

import pytest

from database.models import User
from database.repository.user import UserRepository
from service.user import UserService


@pytest.fixture
def mock_user_repo():
    """Fixture for a mocked UserRepository."""
    repo = Mock(spec=UserRepository)
    repo.get_user_by_telegram_id = AsyncMock()
    repo.create_user = AsyncMock()
    repo.update_user = AsyncMock()
    return repo


class TestUserService:
    """Test cases for UserService"""

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id(self, mock_async_session, mock_user_repo):
        """Test getting a user by Telegram ID delegates to the repository."""
        # Arrange
        user_service = UserService(user_repository=mock_user_repo)
        mock_user = Mock(spec=User)
        mock_user_repo.get_user_by_telegram_id.return_value = mock_user

        # Act
        result = await user_service.get_user_by_telegram_id(
            session=mock_async_session,
            telegram_id=123
        )

        # Assert
        mock_user_repo.get_user_by_telegram_id.assert_called_once_with(mock_async_session, 123)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_create_user(self, mock_async_session, mock_user_repo):
        """Test creating a user delegates to the repository."""
        # Arrange
        user_service = UserService(user_repository=mock_user_repo)
        mock_user = Mock(spec=User)
        mock_user_repo.create_user.return_value = mock_user

        # Act
        result = await user_service.create_user(
            session=mock_async_session,
            telegram_id=123,
            language_code='en',
            timezone_offset=180
        )

        # Assert
        mock_user_repo.create_user.assert_called_once_with(
            mock_async_session, 123, 'en', 180
        )
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_or_create_user_existing(self, mock_async_session, mock_user_repo):
        """Test get_or_create_user returns existing user."""
        # Arrange
        user_service = UserService(user_repository=mock_user_repo)
        mock_user = Mock(spec=User)
        mock_user_repo.get_user_by_telegram_id.return_value = mock_user

        # Act
        result = await user_service.get_or_create_user(
            session=mock_async_session,
            telegram_id=123
        )

        # Assert
        mock_user_repo.get_user_by_telegram_id.assert_called_once_with(mock_async_session, 123)
        mock_user_repo.create_user.assert_not_called()
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_or_create_user_new(self, mock_async_session, mock_user_repo):
        """Test get_or_create_user creates a new user if not exists."""
        # Arrange
        user_service = UserService(user_repository=mock_user_repo)
        mock_user = Mock(spec=User)
        mock_user_repo.get_user_by_telegram_id.return_value = None  # Simulate user not found
        mock_user_repo.create_user.return_value = mock_user

        # Act
        result = await user_service.get_or_create_user(
            session=mock_async_session,
            telegram_id=123,
            language_code='fr',
            timezone_offset=120
        )

        # Assert
        mock_user_repo.get_user_by_telegram_id.assert_called_once_with(mock_async_session, 123)
        mock_user_repo.create_user.assert_called_once_with(mock_async_session, 123, 'fr', 120)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_set_user_hour_timezone(self, mock_async_session, mock_user_repo):
        """Test setting user timezone in hours."""
        # Arrange
        user_service = UserService(user_repository=mock_user_repo)
        mock_user = Mock(spec=User)
        mock_user.timezone_offset = 0
        mock_user_repo.get_user_by_telegram_id.return_value = mock_user

        # Act
        await user_service.set_user_hour_timezone(
            session=mock_async_session,
            telegram_id=123,
            timezone_offset=3
        )

        # Assert
        assert mock_user.timezone_offset == 180  # 3 * 60
        mock_user_repo.update_user.assert_called_once_with(mock_async_session, mock_user)

    @pytest.mark.asyncio
    async def test_set_user_minute_timezone(self, mock_async_session, mock_user_repo):
        """Test setting user timezone in minutes."""
        # Arrange
        user_service = UserService(user_repository=mock_user_repo)
        mock_user = Mock(spec=User)
        mock_user.timezone_offset = 120  # +2 hours
        mock_user_repo.get_user_by_telegram_id.return_value = mock_user

        # Act
        await user_service.set_user_minute_timezone(
            session=mock_async_session,
            telegram_id=123,
            timezone_minutes=45
        )

        # Assert
        assert mock_user.timezone_offset == 165  # 120 + 45
        mock_user_repo.update_user.assert_called_once_with(mock_async_session, mock_user)
