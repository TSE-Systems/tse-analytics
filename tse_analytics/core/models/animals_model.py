from collections.abc import Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.core.data.shared import Animal


class AnimalsModel(QAbstractTableModel):
    header = ("Animal", "Box", "Weight", "Text1", "Text2", "Text3")

    def __init__(self, items: Sequence[Animal], parent=None):
        super().__init__(parent)

        self.items = items

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        item = self.items[index.row()]
        match index.column():
            case 0:
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.id
                elif role == Qt.ItemDataRole.CheckStateRole:
                    return Qt.CheckState.Checked if item.enabled else Qt.CheckState.Unchecked
            case 1:
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.box
            case 2:
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.weight
            case 3:
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.text1
            case 4:
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.text2
            case 5:
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.text3

    def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole):
        if index.column() == 0 and role == Qt.ItemDataRole.CheckStateRole:
            item = self.items[index.row()]
            item.enabled = value == Qt.CheckState.Checked.value
            return True

    def flags(self, index: QModelIndex):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)
