from functools import partial

from PySide6.QtCore import QItemSelection, QModelIndex, QSize, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QInputDialog,
    QLineEdit,
    QMenu,
    QTreeView,
    QWidget, QDialog,
)

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import SelectedTreeNodeChangedMessage
from tse_analytics.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.views.datasets_merge_dialog import DatasetsMergeDialog
from tse_datatools.data.dataset import Dataset
from tse_datatools.helpers.dataset_merger import MergingMode


class DatasetsTreeView(QTreeView):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        pal = self.palette()
        pal.setColor(QPalette.Inactive, QPalette.Highlight, pal.color(QPalette.Active, QPalette.Highlight))
        pal.setColor(QPalette.Inactive, QPalette.HighlightedText, pal.color(QPalette.Active, QPalette.HighlightedText))
        self.setPalette(pal)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
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

            action = menu.addAction("Merge datasets...")
            action.triggered.connect(partial(self._merge_datasets, indexes))

            action = menu.addAction("Remove datasets")
            action.triggered.connect(partial(self._remove, indexes))

        menu.exec_(self.viewport().mapToGlobal(position))

    def _merge_datasets(self, indexes: list[QModelIndex]):
        checked_datasets: list[Dataset] = []
        items = self.model().workspace_tree_item.child_items
        for item in items:
            if item.checked:
                checked_datasets.append(item.dataset)

        dlg = DatasetsMergeDialog(self)
        result = dlg.exec()
        if result == QDialog.DialogCode.Accepted:
            new_dataset_name = dlg.lineEditName.text()
            merging_mode = MergingMode.CONCATENATE if dlg.radioButtonConcatenation.isChecked() else MergingMode.OVERLAP
            Manager.merge_datasets(new_dataset_name, checked_datasets, merging_mode)
            # uncheck all datasets
            items = self.model().workspace_tree_item.child_items
            for item in items:
                item.checked = False

    def _adjust_dataset_time(self, indexes: list[QModelIndex]):
        delta, ok = QInputDialog.getText(self, "Enter time delta", "Delta", QLineEdit.EchoMode.Normal, "1 d")
        if ok:
            Manager.data.adjust_dataset_time(indexes, delta)

    def _remove(self, indexes: list[QModelIndex]):
        Manager.remove_dataset(indexes)

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

    def minimumSizeHint(self):
        return QSize(200, 40)
