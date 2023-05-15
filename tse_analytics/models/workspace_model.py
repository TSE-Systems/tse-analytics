import pickle
from typing import Optional

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal

from tse_analytics.models.calo_details_tree_item import CaloDetailsTreeItem
from tse_analytics.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.models.tree_item import TreeItem
from tse_analytics.models.workspace_tree_item import WorkspaceTreeItem
from tse_datatools.data.calo_details import CaloDetails
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.workspace import Workspace


class WorkspaceModel(QAbstractItemModel):
    checked_item_changed = Signal(TreeItem)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.workspace = Workspace("Workspace")
        self.workspace_tree_item = WorkspaceTreeItem(self.workspace)

    def rowCount(self, index: QModelIndex):
        if index.isValid():
            return index.internalPointer().child_count()
        return self.workspace_tree_item.child_count()

    def addChild(self, node, parent: Optional[QModelIndex] = None):
        if not parent or not parent.isValid():
            parent = self.workspace_tree_item
        else:
            parent = parent.internalPointer()
        parent.add_child(node)

    def removeRow(self, row: int, parent: Optional[QModelIndex] = None):
        if not parent or not parent.isValid():
            # parent is not valid when it is the root node, since the "parent"
            # method returns an empty QModelIndex
            parentNode = self.workspace_tree_item
        else:
            parentNode = parent.internalPointer()  # the node
        return parentNode.remove_child(row)

    def getItem(self, index: QModelIndex):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.workspace_tree_item

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return self.createIndex(p.row(), 0, p)
        return QModelIndex()

    def columnCount(self, index: QModelIndex):
        if index.isValid():
            return index.internalPointer().column_count()
        return self.workspace_tree_item.column_count()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = None):
        if not index.isValid():
            return None

        item = self.getItem(index)

        if role == Qt.ItemDataRole.ToolTipRole:
            if index.column() == 0:
                return item.tooltip

        if role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 0:
                return item.icon

        if role == Qt.ItemDataRole.ForegroundRole:
            if index.column() == 0:
                return item.foreground

        if role == Qt.ItemDataRole.CheckStateRole:
            if index.column() == 0:
                return Qt.CheckState.Checked if item.checked else Qt.CheckState.Unchecked

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if index.column() != 1:
                return item.data(index.column())

        return None

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        item = self.getItem(index)
        if role == Qt.ItemDataRole.CheckStateRole:
            item.checked = not item.checked
            self.checked_item_changed.emit(item)
            return True
        else:
            return False

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return 0
        item = index.internalPointer()
        return item.flags(index.column())

    def headerData(self, section, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.workspace_tree_item.column_names[section]

        return None

    def load_workspace(self, path: str):
        self.beginResetModel()
        with open(path, "rb") as file:
            self.workspace = pickle.load(file)
            self.workspace_tree_item = WorkspaceTreeItem(self.workspace)
            for dataset in self.workspace.datasets:
                dataset_tree_item = DatasetTreeItem(dataset)

                if hasattr(dataset, "calo_details") and dataset.calo_details is not None:
                    calo_details_tree_item = CaloDetailsTreeItem(dataset.calo_details)
                    dataset_tree_item.add_child(calo_details_tree_item)

                self.workspace_tree_item.add_child(dataset_tree_item)
        self.endResetModel()

    def save_workspace(self, path: str):
        with open(path, "wb") as file:
            pickle.dump(self.workspace, file)

    def add_dataset(self, dataset: Dataset):
        self.workspace.datasets.append(dataset)
        dataset_tree_item = DatasetTreeItem(dataset)
        self.beginResetModel()
        self.workspace_tree_item.add_child(dataset_tree_item)
        self.endResetModel()

    def add_calo_details(self, dataset_index: QModelIndex, calo_details: CaloDetails):
        dataset_tree_item: DatasetTreeItem = self.getItem(dataset_index)
        calo_details_tree_item = CaloDetailsTreeItem(calo_details)
        self.beginResetModel()
        dataset_tree_item.dataset.calo_details = calo_details
        dataset_tree_item.clear()
        dataset_tree_item.add_child(calo_details_tree_item)
        self.endResetModel()

    def remove_dataset(self, indexes: list[QModelIndex]):
        self.beginResetModel()
        for index in indexes:
            row = index.row()
            self.removeRow(row, parent=index.parent())
            self.workspace.datasets.pop(row)
        self.endResetModel()
