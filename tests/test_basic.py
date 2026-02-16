"""Basic tests for poop tracker bot"""
import pytest
from datetime import date


def test_basic_structure():
    """Test that basic project structure is correct"""
    assert True  # Placeholder test


def test_date_utils():
    """Test date utilities"""
    today = date.today()
    assert isinstance(today, date)


if __name__ == "__main__":
    pytest.main([__file__])