from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QTreeView, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.models.json_model import JsonModel


class InfoWidget(QTreeView, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.horizontalScrollBar().setEnabled(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        # self.setAlternatingRowColors(True)

        self._model = JsonModel()
        self.setModel(self._model)

        messaging.subscribe(self, messaging.SelectedTreeItemChangedMessage, self._on_selected_tree_node_changed)
        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)

    def set_data(self, data: dict):
        self._model.load(data)
        self.resizeColumnToContents(1)

    def _on_selected_tree_node_changed(self, message: messaging.SelectedTreeItemChangedMessage):
        if message.tree_item.meta is not None:
            self.set_data(message.tree_item.meta)
        else:
            self._model.clear()

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        if message.dataset is None:
            self._model.clear()
