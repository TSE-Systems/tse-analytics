import logging
from typing import Optional

from loguru import logger

from PySide6.QtWidgets import QWidget, QTextEdit


class TextEditLogger(logging.Handler):
    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record: logging.LogRecord):
        match record.levelno:
            case logging.INFO:
                color = "black"
            case logging.DEBUG:
                color = "grey"
            case logging.ERROR:
                color = "red"
            case logging.CRITICAL:
                color = "red"
            case logging.WARNING:
                color = "blue"
            case _:
                color = "black"
        self.text_edit.setTextColor(color)
        self.text_edit.append(self.format(record))


class LogWidget(QTextEdit):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        # logging.getLogger().addHandler(TextEditLogger(self))
        logger.add(TextEditLogger(self), level="INFO", colorize=False, backtrace=False, enqueue=True, format="{message}")
