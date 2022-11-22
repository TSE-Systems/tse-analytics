from functools import partial

from PySide6.QtCore import Qt, QModelIndex, QItemSelection
from PySide6.QtWidgets import QTreeView, QWidget, QAbstractItemView, QMenu, QInputDialog, QLineEdit

from tse_analytics.messaging.messages import SelectedTreeNodeChangedMessage
from tse_analytics.core.manager import Manager
from tse_analytics.models.dataset_tree_item import DatasetTreeItem


class DatasetsTreeView(QTreeView):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setModel(Manager.workspace.workspace_model)
        self.customContextMenuRequested.connect(self._open_menu)
        self.selectionModel().selectionChanged.connect(self._treeview_selection_changed)
        self.selectionModel().currentChanged.connect(self._treeview_current_changed)
        self.doubleClicked.connect(self._treeview_double_clicked)

    def _open_menu(self, position):
        indexes = self.selectedIndexes()

        level = None
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QMenu(self)

        if level == 1:
            action = menu.addAction("Adjust time...")
            action.triggered.connect(partial(self._adjust_dataset_time, indexes))

            action = menu.addAction("Merge datasets")
            action.triggered.connect(partial(self._merge_datasets, indexes))

            action = menu.addAction("Remove")
            action.triggered.connect(partial(self._remove, indexes))

        menu.exec_(self.viewport().mapToGlobal(position))

    def _merge_datasets(self, indexes: [QModelIndex]):
        # Manager.data.close_dataset(indexes)
        items = self.model().workspace_tree_item.child_items
        for item in items:
            print(item.checked)

    def _adjust_dataset_time(self, indexes: [QModelIndex]):
        delta, ok = QInputDialog.getText(self, "Enter time delta", "Delta", QLineEdit.EchoMode.Normal, "1 d")
        if ok:
            Manager.data.adjust_dataset_time(indexes, delta)

    def _remove(self, indexes: [QModelIndex]):
        Manager.workspace.remove_dataset(indexes)

    def _treeview_current_changed(self, current: QModelIndex, previous: QModelIndex):
        if current.isValid():
            item = current.model().getItem(current)
            Manager.messenger.broadcast(SelectedTreeNodeChangedMessage(self, item))
            if isinstance(item, DatasetTreeItem):
                Manager.data.set_selected_dataset(item.dataset)

    def _treeview_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        indexes = selected.indexes()

    def _treeview_double_clicked(self, index: QModelIndex):
        if index.isValid():
            item = index.model().getItem(index)
            # if isinstance(item, DatasetTreeItem) and not item.loaded:
            #     self._load([index])
