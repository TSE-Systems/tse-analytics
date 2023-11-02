from pathlib import PurePath
from typing import Optional

import markdown
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

        self.md = markdown.Markdown(
            extensions=["pymdownx.b64"],
            extension_configs={
                "pymdownx.b64": {
                    "base_path": PurePath(__file__).parent.parent.parent / "docs"
                }
            }
        )

        self.setReadOnly(True)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, ShowHelpMessage, self._on_show_help)

    def _on_show_help(self, message: ShowHelpMessage):
        html = self.md.convert(message.content)
        self.setHtml(html)
