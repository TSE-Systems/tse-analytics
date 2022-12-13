from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QVBoxLayout, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import ClearDataMessage, DatasetChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.selection.animals.animals_table_view import AnimalsTableView


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
        messenger.subscribe(self, ClearDataMessage, self._on_clear_data)

    def clear(self):
        self.table_view.clear()

    def _on_clear_data(self, message: ClearDataMessage):
        self.clear()

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.table_view.set_data(message.data.animals)

    def minimumSizeHint(self):
        return QSize(200, 40)
