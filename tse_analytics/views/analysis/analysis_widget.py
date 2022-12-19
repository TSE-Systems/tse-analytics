import os.path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolBar, QToolButton, QVBoxLayout, QWidget, QPushButton

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import (
    ClearDataMessage,
    DatasetChangedMessage,
    ShowHelpMessage,
)
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_datatools.data.variable import Variable


class AnalysisWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        MessengerListener.__init__(self)
        self.register_to_messenger(Manager.messenger)

        self.help_path: Optional[str] = None

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        help_button = QToolButton()
        help_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        help_button.setToolTip("Show help")
        help_button.setIcon(QIcon(":/icons/icons8-help-16.png"))
        help_button.clicked.connect(self.__show_help)
        self.toolbar.addWidget(help_button)

        analyze_button = QPushButton("Analyze")
        analyze_button.clicked.connect(self._analyze)
        self.toolbar.addWidget(analyze_button)

        self.toolbar.addSeparator()

        self.layout().addWidget(self.toolbar)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self._on_clear_data)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.update_variables(message.data.variables)

    def _on_clear_data(self, message: ClearDataMessage):
        self.clear()

    def clear(self):
        pass

    def _analyze(self):
        pass

    def update_variables(self, variables: dict[str, Variable]):
        pass

    def __show_help(self):
        if self.help_path is not None and os.path.exists(self.help_path):
            with open(self.help_path, "r") as file:
                content = file.read().rstrip()
                if content is not None:
                    Manager.messenger.broadcast(ShowHelpMessage(self, content))
