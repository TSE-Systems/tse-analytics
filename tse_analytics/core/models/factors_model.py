from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import Factor
from tse_analytics.core.models.tree_item import TreeItem


class FactorsModel(QAbstractItemModel):
    def __init__(self, factors: dict[str, Factor], widget: QWidget, parent=None):
        super().__init__(parent)

        self.factors = factors
        self.widget = widget

        self.root_item = TreeItem("Root Item")
        self.setupModelData()

    def setupModelData(self):
        self.beginResetModel()
        self.root_item.clear()
        for factor in self.factors.values():
            factor_tree_item = TreeItem(factor.name)
            for level in factor.levels:
                factor_tree_item.add_child(TreeItem(level.name, color=level.color))
            self.root_item.add_child(factor_tree_item)
        self.endResetModel()

    def getItem(self, index: QModelIndex):
        """Helper method to get the TreeNode from a QModelIndex."""
        if index.isValid():
            item = index.internalPointer()
            if item is not None:
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
        if not index.isValid():
            return None

        item = self.getItem(index)
        if role == Qt.ItemDataRole.DisplayRole:
            return item.name
        elif role == Qt.ItemDataRole.EditRole:
            return item
        elif role == Qt.ItemDataRole.DecorationRole and item.color is not None:
            return QColor(item.color)

        return None

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        if role == Qt.ItemDataRole.EditRole and value is not None:
            item = self.getItem(index)
            item.color = value.name()
            factor = self.factors[item.parent_item().name]
            for level in factor.levels:
                if level.name == item.name:
                    level.color = item.color
                    break
            return True

        return False

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        item = self.getItem(index)
        if item.color is not None:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        else:
            return Qt.ItemFlag.ItemIsEnabled

    def headerData(self, section, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        return None
