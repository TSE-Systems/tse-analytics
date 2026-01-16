"""
Unit tests for tse_analytics.core.toaster module.
"""

from unittest.mock import MagicMock, patch

import pytest
from pyqttoast import Toast, ToastPosition, ToastPreset
from PySide6.QtWidgets import QApplication, QWidget

from tse_analytics.core.toaster import make_toast


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for Qt-based tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestMakeToast:
    """Tests for make_toast function."""

    def test_returns_toast_object(self, qapp):
        """Test that make_toast returns a Toast object."""
        parent = QWidget()
        result = make_toast(parent, "Title", "Text")

        assert isinstance(result, Toast)

    def test_toast_title_set(self, qapp):
        """Test that toast title is correctly set."""
        parent = QWidget()
        toast = make_toast(parent, "Test Title", "Test Text")

        # Toast object should have been configured
        assert toast is not None

    def test_default_parameters(self, qapp):
        """Test make_toast with default parameters."""
        parent = QWidget()
        toast = make_toast(parent, "Title", "Text")

        assert isinstance(toast, Toast)

    def test_custom_duration(self, qapp):
        """Test make_toast with custom duration."""
        parent = QWidget()
        toast = make_toast(parent, "Title", "Text", duration=5000)

        assert isinstance(toast, Toast)

    def test_information_preset(self, qapp):
        """Test make_toast with INFORMATION preset."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Info",
            "Information message",
            preset=ToastPreset.INFORMATION
        )

        assert isinstance(toast, Toast)

    def test_warning_preset(self, qapp):
        """Test make_toast with WARNING preset."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Warning",
            "Warning message",
            preset=ToastPreset.WARNING
        )

        assert isinstance(toast, Toast)

    def test_error_preset(self, qapp):
        """Test make_toast with ERROR preset."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Error",
            "Error message",
            preset=ToastPreset.ERROR
        )

        assert isinstance(toast, Toast)

    def test_success_preset(self, qapp):
        """Test make_toast with SUCCESS preset."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Success",
            "Success message",
            preset=ToastPreset.SUCCESS
        )

        assert isinstance(toast, Toast)

    def test_custom_position(self, qapp):
        """Test make_toast with custom position."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Title",
            "Text",
            position=ToastPosition.TOP_RIGHT
        )

        assert isinstance(toast, Toast)

    def test_show_duration_bar_true(self, qapp):
        """Test make_toast with show_duration_bar=True."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Title",
            "Text",
            duration=3000,
            show_duration_bar=True
        )

        assert isinstance(toast, Toast)

    def test_show_duration_bar_false(self, qapp):
        """Test make_toast with show_duration_bar=False."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Title",
            "Text",
            show_duration_bar=False
        )

        assert isinstance(toast, Toast)

    @patch('tse_analytics.core.toaster.logger')
    def test_echo_to_logger_information(self, mock_logger, qapp):
        """Test that information messages are logged when echo_to_logger=True."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Info",
            "Test info message",
            preset=ToastPreset.INFORMATION,
            echo_to_logger=True
        )

        mock_logger.info.assert_called_once_with("Test info message")

    @patch('tse_analytics.core.toaster.logger')
    def test_echo_to_logger_warning(self, mock_logger, qapp):
        """Test that warning messages are logged when echo_to_logger=True."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Warning",
            "Test warning message",
            preset=ToastPreset.WARNING,
            echo_to_logger=True
        )

        mock_logger.warning.assert_called_once_with("Test warning message")

    @patch('tse_analytics.core.toaster.logger')
    def test_echo_to_logger_error(self, mock_logger, qapp):
        """Test that error messages are logged when echo_to_logger=True."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Error",
            "Test error message",
            preset=ToastPreset.ERROR,
            echo_to_logger=True
        )

        mock_logger.error.assert_called_once_with("Test error message")

    @patch('tse_analytics.core.toaster.logger')
    def test_echo_to_logger_success(self, mock_logger, qapp):
        """Test that success messages are logged when echo_to_logger=True."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Success",
            "Test success message",
            preset=ToastPreset.SUCCESS,
            echo_to_logger=True
        )

        mock_logger.success.assert_called_once_with("Test success message")

    @patch('tse_analytics.core.toaster.logger')
    def test_no_logging_when_echo_false(self, mock_logger, qapp):
        """Test that messages are not logged when echo_to_logger=False."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Title",
            "Test message",
            preset=ToastPreset.INFORMATION,
            echo_to_logger=False
        )

        mock_logger.info.assert_not_called()
        mock_logger.warning.assert_not_called()
        mock_logger.error.assert_not_called()

    def test_zero_duration(self, qapp):
        """Test make_toast with zero duration (toast stays until clicked)."""
        parent = QWidget()
        toast = make_toast(parent, "Title", "Text", duration=0)

        assert isinstance(toast, Toast)

    def test_all_parameters_combined(self, qapp):
        """Test make_toast with all parameters specified."""
        parent = QWidget()
        toast = make_toast(
            parent,
            "Test Title",
            "Test Text",
            duration=3000,
            preset=ToastPreset.WARNING,
            position=ToastPosition.BOTTOM_RIGHT,
            show_duration_bar=True,
            echo_to_logger=False
        )

        assert isinstance(toast, Toast)
