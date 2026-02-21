"""Unit tests for UserService"""
from unittest.mock import AsyncMock, Mock, patch

import pytest

from database.models import User
from service.user import UserService


class TestUserService:
    """Test cases for UserService"""

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_user_exists(self, mock_async_session):
        """Test getting existing user by Telegram ID"""
        # Arrange
        mock_user = Mock(spec=User)

        with patch('service.user.UserRepository.get_user_by_telegram_id') as mock_get:
            mock_get.return_value = mock_user

            # Act
            result = await UserService.get_user_by_telegram_id(
                session=mock_async_session,
                telegram_id=123
            )

            # Assert
            mock_get.assert_called_once_with(mock_async_session, 123)
            assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_user_not_exists(self, mock_async_session):
        """Test getting non-existing user returns None"""
        # Arrange
        with patch('service.user.UserRepository.get_user_by_telegram_id') as mock_get:
            mock_get.return_value = None

            # Act
            result = await UserService.get_user_by_telegram_id(
                session=mock_async_session,
                telegram_id=999
            )

            # Assert
            mock_get.assert_called_once_with(mock_async_session, 999)
            assert result is None

    @pytest.mark.asyncio
    async def test_create_user_default_values(self, mock_async_session):
        """Test creating user with default values"""
        # Arrange
        mock_user = Mock(spec=User)

        with patch('service.user.UserRepository.create_user') as mock_create:
            mock_create.return_value = mock_user

            # Act
            result = await UserService.create_user(
                session=mock_async_session,
                telegram_id=123
            )

            # Assert
            mock_create.assert_called_once_with(
                mock_async_session, 123, 'ru', 0
            )
            assert result == mock_user

    @pytest.mark.asyncio
    async def test_create_user_custom_values(self, mock_async_session):
        """Test creating user with custom values"""
        # Arrange
        mock_user = Mock(spec=User)

        with patch('service.user.UserRepository.create_user') as mock_create:
            mock_create.return_value = mock_user

            # Act
            result = await UserService.create_user(
                session=mock_async_session,
                telegram_id=123,
                language_code='en',
                timezone_offset=180
            )

            # Assert
            mock_create.assert_called_once_with(
                mock_async_session, 123, 'en', 180
            )
            assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_or_create_user_existing(self, mock_async_session):
        """Test get_or_create_user when user already exists"""
        # Arrange
        mock_user = Mock(spec=User)

        with patch('service.user.UserService.get_user_by_telegram_id') as mock_get:
            mock_get.return_value = mock_user

            # Act
            result = await UserService.get_or_create_user(
                session=mock_async_session,
                telegram_id=123
            )

            # Assert
            mock_get.assert_called_once_with(mock_async_session, 123)
            assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_or_create_user_new(self, mock_async_session):
        """Test get_or_create_user when creating new user"""
        # Arrange
        mock_user = Mock(spec=User)

        with patch('service.user.UserService.get_user_by_telegram_id') as mock_get:
            mock_get.return_value = None
            with patch('service.user.UserService.create_user') as mock_create:
                mock_create.return_value = mock_user

                # Act
                result = await UserService.get_or_create_user(
                    session=mock_async_session,
                    telegram_id=123
                )

                # Assert
                mock_get.assert_called_once_with(mock_async_session, 123)
                mock_create.assert_called_once_with(mock_async_session, 123, 'ru', None)
                assert result == mock_user

    @pytest.mark.asyncio
    async def test_set_user_hour_timezone(self, mock_async_session):
        """Test setting user timezone in hours"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.timezone_offset = 0

        with patch('service.user.UserService.get_user_by_telegram_id') as mock_get:
            mock_get.return_value = mock_user
            with patch('service.user.UserRepository.update_user') as mock_update:
                mock_update.return_value = mock_user

                # Act
                result = await UserService.set_user_hour_timezone(
                    session=mock_async_session,
                    telegram_id=123,
                    timezone_offset=3
                )

                # Assert
                mock_get.assert_called_once_with(mock_async_session, 123)
                assert mock_user.timezone_offset == 180  # 3 hours * 60 minutes
                mock_update.assert_called_once_with(mock_async_session, mock_user)
                assert result == mock_user

    @pytest.mark.asyncio
    async def test_set_user_hour_timezone_user_not_found(self, mock_async_session):
        """Test setting timezone for non-existing user returns None"""
        # Arrange
        with patch('service.user.UserService.get_user_by_telegram_id') as mock_get:
            mock_get.return_value = None

            # Act
            result = await UserService.set_user_hour_timezone(
                session=mock_async_session,
                telegram_id=999,
                timezone_offset=3
            )

            # Assert
            mock_get.assert_called_once_with(mock_async_session, 999)
            assert result is None

    @pytest.mark.asyncio
    async def test_set_user_minute_timezone_positive_hours(self, mock_async_session):
        """Test setting minute timezone offset when base hours are positive"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.timezone_offset = 120  # +2 hours

        with patch('service.user.UserService.get_user_by_telegram_id') as mock_get:
            mock_get.return_value = mock_user
            with patch('service.user.UserRepository.update_user') as mock_update:
                mock_update.return_value = mock_user

                # Act
                result = await UserService.set_user_minute_timezone(
                    session=mock_async_session,
                    telegram_id=123,
                    timezone_minutes=30
                )

                # Assert
                mock_get.assert_called_once_with(mock_async_session, 123)
                assert mock_user.timezone_offset == 150  # 120 + 30
                mock_update.assert_called_once_with(mock_async_session, mock_user)
                assert result == mock_user

    @pytest.mark.asyncio
    async def test_set_user_minute_timezone_negative_hours(self, mock_async_session):
        """Test setting minute timezone offset when base hours are negative"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.timezone_offset = -120  # -2 hours

        with patch('service.user.UserService.get_user_by_telegram_id') as mock_get:
            mock_get.return_value = mock_user
            with patch('service.user.UserRepository.update_user') as mock_update:
                mock_update.return_value = mock_user

                # Act
                result = await UserService.set_user_minute_timezone(
                    session=mock_async_session,
                    telegram_id=123,
                    timezone_minutes=30
                )

                # Assert
                mock_get.assert_called_once_with(mock_async_session, 123)
                assert mock_user.timezone_offset == -150  # -120 - 30
                mock_update.assert_called_once_with(mock_async_session, mock_user)
                assert result == mock_user

    @pytest.mark.asyncio
    async def test_set_user_minute_timezone_no_change(self, mock_async_session):
        """Test setting minute timezone when offset doesn't change"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.timezone_offset = 120  # +2 hours

        with patch('service.user.UserService.get_user_by_telegram_id') as mock_get:
            mock_get.return_value = mock_user
            with patch('service.user.UserRepository.update_user') as mock_update:
                mock_update.return_value = mock_user

                # Act
                result = await UserService.set_user_minute_timezone(
                    session=mock_async_session,
                    telegram_id=123,
                    timezone_minutes=0
                )

                # Assert
                mock_get.assert_called_once_with(mock_async_session, 123)
                # Offset should remain 120 (120 + 0)
                assert mock_user.timezone_offset == 120
                mock_update.assert_not_called()  # No update when offset doesn't change
                assert result == mock_user

    @pytest.mark.asyncio
    async def test_set_user_minute_timezone_user_not_found(self, mock_async_session):
        """Test setting minute timezone for non-existing user returns None"""
        # Arrange
        with patch('service.user.UserService.get_user_by_telegram_id') as mock_get:
            mock_get.return_value = None

            # Act
            result = await UserService.set_user_minute_timezone(
                session=mock_async_session,
                telegram_id=999,
                timezone_minutes=30
            )

            # Assert
            mock_get.assert_called_once_with(mock_async_session, 999)
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
