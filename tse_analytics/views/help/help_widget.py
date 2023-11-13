from typing import Optional

from PySide6.QtWidgets import QTextEdit, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import ShowHelpMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener


class HelpWidget(QTextEdit, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)
        self.register_to_messenger(Manager.messenger)

        self.setReadOnly(True)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, ShowHelpMessage, self._on_show_help)

    def _on_show_help(self, message: ShowHelpMessage):
        content = message.content.replace("../docs/", "docs/")
        self.setMarkdown(content)
