import logging

from loguru import logger
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QTextEdit, QToolBar, QVBoxLayout, QWidget

"""
Log widget module for displaying application logs in the UI.

This module provides widgets for displaying and managing log messages within the application,
with color-coded formatting based on log levels.
"""


class TextEditLogger(logging.Handler):
    """
    Custom logging handler that formats and displays log messages in a QTextEdit widget.

    This handler applies color formatting to log messages based on their log level
    and appends them to the specified QTextEdit widget.
    """

    def __init__(self, text_edit: QTextEdit):
        """
        Initialize the TextEditLogger with a QTextEdit widget.

        Args:
            text_edit (QTextEdit): The QTextEdit widget where log messages will be displayed
        """
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record: logging.LogRecord):
        """
        Process a log record and display it in the QTextEdit with appropriate color formatting.

        Args:
            record (logging.LogRecord): The log record to be processed and displayed
        """
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
                color = "darkorange"
            case _:
                color = "black"
        self.text_edit.setTextColor(color)
        self.text_edit.append(self.format(record))


class LogWidget(QWidget):
    """
    Widget for displaying and managing application logs.

    This widget provides a text area for displaying log messages with a toolbar
    that includes actions such as clearing the log display.
    """

    def __init__(self, parent: QWidget | None = None):
        """
        Initialize the LogWidget with optional parent widget.

        Args:
            parent (QWidget | None, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar(
            "Log Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.toolbar.addAction(QIcon(":/icons/icons8-erase-16.png"), "Clear log").triggered.connect(self._clear_log)

        self._layout.addWidget(self.toolbar)

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
        self._layout.addWidget(self.text_edit)

    def _clear_log(self):
        """
        Clear all log messages from the text edit widget.
        """
        self.text_edit.clear()
