from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.datatable_tree_item import DatatableTreeItem
from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.core.models.workspace_tree_item import WorkspaceTreeItem


class WorkspaceModel(QAbstractItemModel):
    checkedItemChanged = Signal(TreeItem, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.workspace = Workspace("Workspace")
        self.workspace_tree_item = WorkspaceTreeItem(self.workspace)

    def addChild(self, node, parent: QModelIndex | None = None):
        if not parent or not parent.isValid():
            parent = self.workspace_tree_item
        else:
            parent = parent.internalPointer()
        parent.add_child(node)

    def removeRow(self, row: int, parent: QModelIndex | None = None):
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

    def parent(self, child: QModelIndex) -> QModelIndex:
        if child.isValid():
            p = child.internalPointer().parent()
            if p:
                return self.createIndex(p.row(), 0, p)
        return QModelIndex()

    def rowCount(self, parent: QModelIndex = ...):
        if parent.isValid():
            return parent.internalPointer().child_count()
        return self.workspace_tree_item.child_count()

    def columnCount(self, parent: QModelIndex = ...):
        if parent.isValid():
            return parent.internalPointer().column_count()
        return self.workspace_tree_item.column_count()

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
        item = self.getItem(index)
        if role == Qt.ItemDataRole.CheckStateRole:
            item.checked = not item.checked
            self.checkedItemChanged.emit(item, item.checked)
            return True
        else:
            return False

    def flags(self, index: QModelIndex):
        item = index.internalPointer()
        return item.flags(index.column())

    def headerData(self, section, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.workspace_tree_item.column_names[section]

        return None

    def set_workspace(self, workspace: Workspace):
        self.beginResetModel()
        self.workspace = workspace
        self.workspace_tree_item = WorkspaceTreeItem(self.workspace)
        for dataset in self.workspace.datasets.values():
            dataset_tree_item = DatasetTreeItem(dataset)
            dataset.add_children_tree_items(dataset_tree_item)
            self.workspace_tree_item.add_child(dataset_tree_item)
        self.endResetModel()

    def add_dataset(self, dataset: Dataset):
        self.workspace.datasets[dataset.id] = dataset
        dataset_tree_item = DatasetTreeItem(dataset)
        dataset.add_children_tree_items(dataset_tree_item)
        self.beginResetModel()
        self.workspace_tree_item.add_child(dataset_tree_item)
        self.endResetModel()

    def add_dataset_child_items(self, dataset_index: QModelIndex):
        dataset_tree_item: DatasetTreeItem = self.getItem(dataset_index)
        self.beginResetModel()
        dataset_tree_item.dataset.add_children_tree_items(dataset_tree_item)
        self.endResetModel()

    def add_datatable(self, datatable: Datatable):
        for child_item in self.workspace_tree_item.child_items:
            if isinstance(child_item, DatasetTreeItem):
                if datatable.dataset == child_item.dataset:
                    self.beginResetModel()
                    child_item.add_child(DatatableTreeItem(datatable))
                    self.endResetModel()
                    return

    def remove_item(self, indexes: list[QModelIndex]):
        self.beginResetModel()
        for index in indexes:
            row = index.row()
            self.removeRow(row, parent=index.parent())
        self.endResetModel()
