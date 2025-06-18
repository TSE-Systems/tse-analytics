"""
Toast notification module for TSE Analytics.

This module provides a function for creating and displaying toast notifications
in the application using the pyqttoast library.
"""

from loguru import logger
from pyqttoast import Toast, ToastPosition, ToastPreset
from PySide6.QtWidgets import QWidget


def make_toast(
    parent: QWidget,
    title: str,
    text: str,
    duration=0,
    preset=ToastPreset.INFORMATION,
    position=ToastPosition.CENTER,
    show_duration_bar=False,
    echo_to_logger=False,
) -> Toast:
    """
    Create and configure a toast notification.

    This function creates a toast notification with the specified parameters and
    optionally logs the message to the logger.

    Args:
        parent: The parent widget for the toast notification.
        title: The title of the toast notification.
        text: The main text of the toast notification.
        duration: The duration in milliseconds for which the toast is displayed.
            If 0, the toast will stay until clicked.
        preset: The preset style for the toast (INFORMATION, WARNING, ERROR, SUCCESS).
        position: The position of the toast on the screen.
        show_duration_bar: Whether to show a progress bar indicating the remaining duration.
        echo_to_logger: Whether to also log the message to the logger.

    Returns:
        A configured Toast object that can be shown with the show() method.
    """
    toast = Toast(parent)
    toast.setTitle(title)
    toast.setText(text)
    toast.setDuration(duration)
    toast.applyPreset(preset)
    toast.setPosition(position)
    toast.setShowCloseButton(False)
    toast.setShowDurationBar(show_duration_bar)
    toast.setStayOnTop(False)
    if echo_to_logger:
        match preset:
            case ToastPreset.INFORMATION:
                logger.info(text)
            case ToastPreset.WARNING:
                logger.warning(text)
            case ToastPreset.ERROR:
                logger.error(text)
            case ToastPreset.SUCCESS:
                logger.success(text)
            case _:
                logger.info(text)
    return toast
