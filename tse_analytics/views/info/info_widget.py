from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QTreeView, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.datatable_tree_item import DatatableTreeItem
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
        if isinstance(message.tree_item, DatasetTreeItem):
            self.set_data(message.tree_item.dataset.metadata)
        elif isinstance(message.tree_item, DatatableTreeItem):
            self.set_data(message.tree_item.datatable.dataset.metadata)

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        if message.dataset is None:
            self._model.clear()
