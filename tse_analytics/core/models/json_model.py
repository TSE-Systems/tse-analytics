from typing import Any

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, QPersistentModelIndex, Qt

from tse_analytics.core.models.json_tree_item import TreeItem


class JsonModel(QAbstractItemModel):
    """
    An editable model for representing JSON data in a tree structure.

    This model provides a hierarchical view of JSON data with support for
    displaying and editing the key-value pairs. It uses TreeItem instances
    to represent each node in the JSON structure.
    """

    def __init__(self, parent: QObject | None = None):
        """
        Initialize the JSON model.

        Args:
            parent (QObject, optional): The parent object. Defaults to None.
        """
        super().__init__(parent)

        self._rootItem = TreeItem()
        self._headers = ("key", "value")

    def clear(self):
        """Clear data from the model"""
        self.load({})

    def load(self, document: dict):
        """Load model from a nested dictionary returned by json.loads()

        Arguments:
            document (dict): JSON-compatible dictionary
        """

        assert isinstance(document, dict | list | tuple), (
            f"`document` must be of dict, list or tuple, not {type(document)}"
        )

        self.beginResetModel()

        self._rootItem = TreeItem.load(document)
        self._rootItem.value_type = type(document)

        self.endResetModel()

        return True

    def data(self, index: QModelIndex | QPersistentModelIndex, role: Qt.ItemDataRole = ...) -> Any:
        """Override from QAbstractItemModel

        Return data from a json item according index and role

        """
        item = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return item.key

            if index.column() == 1:
                return item.value

        elif role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                return item.value

    def setData(self, index: QModelIndex | QPersistentModelIndex, value: Any, role: Qt.ItemDataRole = ...):
        """Override from QAbstractItemModel

        Set json item according index and role

        Args:
            index (QModelIndex)
            value (Any)
            role (Qt.ItemDataRole)

        """
        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                item = index.internalPointer()
                item.value = str(value)

                self.dataChanged.emit(index, index)
                # if __binding__ in ("PySide", "PyQt4"):
                #     self.dataChanged.emit(index, index)
                # else:
                #     self.dataChanged.emit(index, index, [Qt.EditRole])

                return True

        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...):
        """Override from QAbstractItemModel

        For the JsonModel, it returns only data for columns (orientation = Horizontal)

        """
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        """Override from QAbstractItemModel

        Return index according row, column and parent

        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex = ...):
        """Override from QAbstractItemModel

        Return parent index of index

        """

        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent: QModelIndex = ...):
        """Override from QAbstractItemModel

        Return row count from parent index
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent: QModelIndex = ...):
        """Override from QAbstractItemModel

        Return column number. For the model, it always return 2 columns
        """
        return 2

    def flags(self, index: QModelIndex | QPersistentModelIndex):
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super().flags(index)

        if index.column() == 1:
            return Qt.ItemFlag.ItemIsEditable | flags
        else:
            return flags

    def to_json(self, item=None):
        """
        Convert the model data back to a JSON-compatible Python object.

        This method recursively traverses the tree structure and builds
        a dictionary, list, or primitive value based on the item's type.

        Args:
            item (TreeItem, optional): The starting tree item to convert.
                                      Defaults to the root item.

        Returns:
            dict, list, or primitive value: The JSON-compatible representation
                                           of the model data.
        """
        if item is None:
            item = self._rootItem

        nchild = item.childCount()

        if item.value_type is dict:
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.to_json(ch)
            return document

        elif item.value_type is list:
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.to_json(ch))
            return document

        else:
            return item.value
