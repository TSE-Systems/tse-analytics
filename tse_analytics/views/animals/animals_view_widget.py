from typing import Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.messaging.messages import DatasetRemovedMessage, DatasetUnloadedMessage, DatasetChangedMessage
from tse_analytics.views.animals.animals_table_view import AnimalsTableView


class AnimalsViewWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        self.register_to_messenger(Manager.messenger)

        self.table_view = AnimalsTableView(self)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.table_view)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_dataset_removed)
        messenger.subscribe(self, DatasetUnloadedMessage, self._on_dataset_unloaded)

    def clear(self):
        self.table_view.clear()

    def _on_dataset_removed(self, message: DatasetRemovedMessage):
        self.clear()

    def _on_dataset_unloaded(self, message: DatasetUnloadedMessage):
        self.clear()

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.table_view.set_data(message.data.animals)
