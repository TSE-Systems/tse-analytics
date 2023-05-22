import sys
from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QWidget, QTextEdit


class StdOutEmittingStream(QObject):
    text_written = Signal(str)

    def write(self, text):
        self.text_written.emit(str(text))
        sys.__stdout__.write(text)


class StdErrEmittingStream(QObject):
    text_written = Signal(str)

    def write(self, text):
        self.text_written.emit(str(text))
        sys.__stderr__.write(text)


class LogWidget(QTextEdit):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setReadOnly(True)

        sys.stdout = StdOutEmittingStream()
        sys.stdout.text_written.connect(self.normal_output_written)

        sys.stderr = StdErrEmittingStream()
        sys.stderr.text_written.connect(self.normal_output_written)

    def normal_output_written(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
