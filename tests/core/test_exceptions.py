"""
Unit tests for tse_analytics.core.exceptions module.
"""

import pytest

from tse_analytics.core.exceptions import InvalidMessage, InvalidSubscriber


class TestInvalidSubscriber:
    """Tests for InvalidSubscriber exception."""

    def test_can_be_raised(self):
        """Test that InvalidSubscriber exception can be raised."""
        with pytest.raises(InvalidSubscriber):
            raise InvalidSubscriber("Test error message")

    def test_is_exception(self):
        """Test that InvalidSubscriber is an Exception."""
        assert issubclass(InvalidSubscriber, Exception)

    def test_error_message_preserved(self):
        """Test that error message is preserved when raising."""
        error_msg = "Invalid subscriber provided"
        with pytest.raises(InvalidSubscriber, match=error_msg):
            raise InvalidSubscriber(error_msg)

    def test_can_be_caught_as_exception(self):
        """Test that InvalidSubscriber can be caught as generic Exception."""
        try:
            raise InvalidSubscriber("Test")
        except Exception as e:
            assert isinstance(e, InvalidSubscriber)


class TestInvalidMessage:
    """Tests for InvalidMessage exception."""

    def test_can_be_raised(self):
        """Test that InvalidMessage exception can be raised."""
        with pytest.raises(InvalidMessage):
            raise InvalidMessage("Test error message")

    def test_is_exception(self):
        """Test that InvalidMessage is an Exception."""
        assert issubclass(InvalidMessage, Exception)

    def test_error_message_preserved(self):
        """Test that error message is preserved when raising."""
        error_msg = "Invalid message format"
        with pytest.raises(InvalidMessage, match=error_msg):
            raise InvalidMessage(error_msg)

    def test_can_be_caught_as_exception(self):
        """Test that InvalidMessage can be caught as generic Exception."""
        try:
            raise InvalidMessage("Test")
        except Exception as e:
            assert isinstance(e, InvalidMessage)

    def test_different_from_invalid_subscriber(self):
        """Test that InvalidMessage and InvalidSubscriber are different types."""
        assert InvalidMessage != InvalidSubscriber
        assert not issubclass(InvalidMessage, InvalidSubscriber)
        assert not issubclass(InvalidSubscriber, InvalidMessage)
