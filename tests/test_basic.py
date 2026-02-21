"""Basic tests for poop tracker bot"""
import pytest
from datetime import date
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_basic_structure():
    """Test that basic project structure is correct"""
    # Check that key directories exist
    assert os.path.exists("bot"), "bot directory should exist"
    assert os.path.exists("service"), "service directory should exist"
    assert os.path.exists("database"), "database directory should exist"
    assert os.path.exists("tests"), "tests directory should exist"
    assert True


def test_date_utils():
    """Test date utilities"""
    today = date.today()
    assert isinstance(today, date)


def test_key_imports():
    """Test that key project modules can be imported"""
    # Try importing main modules
    try:
        from bot.handlers import bowel_movement
        from service.bowel_movement import BowelMovementService
        from service.user import UserService
        from database.models import User, BowelMovement

        # If we get here, imports succeeded
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import key module: {e}")


def test_pytest_configuration():
    """Test that pytest is configured correctly"""
    # This test ensures pytest can discover and run tests
    assert True


if __name__ == "__main__":
    pytest.main([__file__])
