from PySide6.QtWidgets import QTextEdit, QWidget

from tse_analytics.core import messaging


class HelpWidget(QTextEdit, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        messaging.subscribe(self, messaging.ShowHelpMessage, self._on_show_help)

        self.setReadOnly(True)

    def _on_show_help(self, message: messaging.ShowHelpMessage):
        self.setMarkdown(message.content)
