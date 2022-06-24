import pickle

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal
import pandas as pd
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.workspace import Workspace

from tse_analytics.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.models.tree_item import TreeItem
from tse_analytics.models.workspace_tree_item import WorkspaceTreeItem


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

    def addChild(self, node, parent: QModelIndex = None):
        if not parent or not parent.isValid():
            parent = self.workspace_tree_item
        else:
            parent = parent.internalPointer()
        parent.add_child(node)

    def removeRow(self, row: int, parent: QModelIndex = None):
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

    def index(self, row, column, parent: QModelIndex = QModelIndex()):
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

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None

        item = self.getItem(index)

        if role == Qt.ToolTipRole:
            if index.column() == 0:
                return item.tooltip

        if role == Qt.DecorationRole:
            if index.column() == 0:
                return item.icon

        if role == Qt.ForegroundRole:
            if index.column() == 0:
                return item.foreground

        if role == Qt.CheckStateRole:
            if index.column() == 0:
                return Qt.Checked if item.checked else Qt.Unchecked

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() != 1:
                return item.data(index.column())

        return None

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        item = self.getItem(index)
        if role == Qt.CheckStateRole:
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

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.workspace_tree_item.column_names[section]

        return None

    def load_workspace(self, path: str):
        self.beginResetModel()
        with open(path, 'rb') as file:
            self.workspace = pickle.load(file)
            self.workspace_tree_item = WorkspaceTreeItem(self.workspace)
            for dataset in self.workspace.datasets:
                dataset.loaded = False
                dataset_tree_item = DatasetTreeItem(dataset)
                self.workspace_tree_item.add_child(dataset_tree_item)
        self.workspace.path = path
        self.endResetModel()

    def save_workspace(self, path: str):
        self.workspace.path = path
        with open(path, 'wb') as file:
            pickle.dump(self.workspace, file)

    def export_to_excel(self, path: str):
        with pd.ExcelWriter(path) as writer:
            self.workspace.datasets[0].calorimetry.df.to_excel(writer, sheet_name='Calorimetry')
            self.workspace.datasets[0].actimot.df.to_excel(writer, sheet_name='Actimot')
            self.workspace.datasets[0].drinkfeed.df.to_excel(writer, sheet_name='DrinkFeed')

    def add_dataset(self, dataset: Dataset):
        self.workspace.datasets.append(dataset)
        dataset_tree_item = DatasetTreeItem(dataset)
        self.beginResetModel()
        self.workspace_tree_item.add_child(dataset_tree_item)
        self.endResetModel()

    def load_dataset(self, indexes: [QModelIndex]):
        self.beginResetModel()
        for index in indexes:
            if index.isValid():
                dataset_tree_item = index.model().getItem(index)
                dataset_tree_item.load()
        self.endResetModel()

    def close_dataset(self, indexes: [QModelIndex]):
        self.beginResetModel()
        for index in indexes:
            if index.isValid():
                item = index.model().getItem(index)
                item.close()
        self.endResetModel()

    def remove_dataset(self, indexes: [QModelIndex]):
        self.beginResetModel()
        for index in indexes:
            row = index.row()
            self.removeRow(row, parent=index.parent())
            self.workspace.datasets.pop(row)
        self.endResetModel()
