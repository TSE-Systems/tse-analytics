from typing import Optional

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetRemovedMessage, DatasetUnloadedMessage, AnimalDataChangedMessage
from tse_analytics.views.settings.binning_widget import BinningWidget


class SettingsWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        self.register_to_messenger(Manager.messenger)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_widget = QTabWidget(self)
        layout.addWidget(self.tab_widget)

        self.binning_widget = BinningWidget(self)
        self.tab_widget.addTab(self.binning_widget, QIcon(":/icons/icons8-time-span-16.png"), 'Binning')

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, AnimalDataChangedMessage, self._on_box_data_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_slide_removed)
        messenger.subscribe(self, DatasetUnloadedMessage, self._on_slide_unloaded)

    def clear(self):
        self.binning_widget.clear()

    def _on_slide_removed(self, message: DatasetRemovedMessage):
        self.clear()

    def _on_slide_unloaded(self, message: DatasetUnloadedMessage):
        self.clear()

    def _on_box_data_changed(self, message: AnimalDataChangedMessage):
        self.binning_widget.set_data(message)
