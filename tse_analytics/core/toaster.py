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
    toast = Toast(parent)
    toast.setTitle(title)
    toast.setText(text)
    toast.setDuration(duration)
    toast.applyPreset(preset)
    toast.setPosition(position)
    toast.setShowCloseButton(False)
    toast.setShowDurationBar(show_duration_bar)
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
