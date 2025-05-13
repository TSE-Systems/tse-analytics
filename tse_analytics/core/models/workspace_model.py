from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal

from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.tree_item import TreeItem


class WorkspaceModel(QAbstractItemModel):
    checkedItemChanged = Signal(TreeItem, bool)

    def __init__(self, workspace: Workspace, parent=None):
        super().__init__(parent)

        self.root_item = TreeItem("Root Item")
        self.setupModelData(workspace)

    def setupModelData(self, workspace: Workspace):
        self.beginResetModel()
        self.root_item.clear()
        for dataset in workspace.datasets.values():
            dataset_tree_item = DatasetTreeItem(dataset)
            dataset.add_children_tree_items(dataset_tree_item)
            self.root_item.add_child(dataset_tree_item)
        self.endResetModel()

    def getItem(self, index: QModelIndex):
        """Helper method to get the TreeNode from a QModelIndex."""
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.root_item  # Return root item for invalid or root index

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            # Pass the child_item as an internal pointer
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return self.createIndex(p.row(), 0, p)
        return QModelIndex()

    def rowCount(self, parent: QModelIndex = ...):
        parent_item = self.getItem(parent)
        return parent_item.child_count()

    def columnCount(self, parent: QModelIndex = ...):
        return 1

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = None):
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
        if role == Qt.ItemDataRole.CheckStateRole:
            item = self.getItem(index)
            item.checked = not item.checked
            self.checkedItemChanged.emit(item, item.checked)
            return True

        return False

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        # Make only the first column checkable
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def headerData(self, section, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        return "Name"
