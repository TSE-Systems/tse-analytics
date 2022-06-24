from typing import Optional

from PySide6.QtWidgets import QTreeView, QWidget
from PySide6.QtCore import Qt

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.messaging.messages import SelectedTreeNodeChangedMessage, DatasetRemovedMessage, DatasetUnloadedMessage
from tse_analytics.models.json_model import JsonModel


class InfoWidget(QTreeView, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        self.horizontalScrollBar().setEnabled(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setAlternatingRowColors(True)

        self._model = JsonModel()
        self.setModel(self._model)

        self.register_to_messenger(Manager.messenger)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, SelectedTreeNodeChangedMessage, self._on_selected_tree_node_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_dataset_removed)
        messenger.subscribe(self, DatasetUnloadedMessage, self._on_dataset_unloaded)

    def _on_dataset_removed(self, message: DatasetRemovedMessage):
        self._model.clear()

    def _on_dataset_unloaded(self, message: DatasetUnloadedMessage):
        self._model.clear()

    def set_data(self, data: dict):
        self._model.load(data)
        self.resizeColumnToContents(1)

    def _on_selected_tree_node_changed(self, message: SelectedTreeNodeChangedMessage):
        if message.node.meta is not None:
            self.set_data(message.node.meta)
        else:
            self._model.clear()
