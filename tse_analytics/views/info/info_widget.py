from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QTreeView, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage, SelectedTreeNodeChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.core.models.json_model import JsonModel


class InfoWidget(QTreeView, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.horizontalScrollBar().setEnabled(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        # self.setAlternatingRowColors(True)

        self._model = JsonModel()
        self.setModel(self._model)

        self.register_to_messenger(Manager.messenger)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, SelectedTreeNodeChangedMessage, self._on_selected_tree_node_changed)
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def set_data(self, data: dict):
        self._model.load(data)
        self.resizeColumnToContents(1)

    def _on_selected_tree_node_changed(self, message: SelectedTreeNodeChangedMessage):
        if message.node.meta is not None:
            self.set_data(message.node.meta)
        else:
            self._model.clear()

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self._model.clear()
