import logging

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from loguru import logger
from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QToolBar


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


class LogWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar(
            "Log Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.toolbar.addAction(QIcon(":/icons/icons8-erase-16.png"), "Clear log").triggered.connect(self._clear_log)

        self.layout.addWidget(self.toolbar)

        self.text_edit = QTextEdit(
            self,
            readOnly=True,
            lineWrapMode=QTextEdit.LineWrapMode.NoWrap,
        )
        logger.add(
            TextEditLogger(self.text_edit),
            level="INFO",
            colorize=False,
            backtrace=False,
            enqueue=True,
            format="{message}",
        )
        self.layout.addWidget(self.text_edit)

    def _clear_log(self):
        self.text_edit.clear()
