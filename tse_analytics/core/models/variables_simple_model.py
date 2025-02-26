from collections.abc import Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.core.data.shared import Variable


class VariablesSimpleModel(QAbstractTableModel):
    header = ("Name", "Unit", "Description")

    def __init__(self, items: Sequence[Variable], parent=None):
        super().__init__(parent)

        self._items = items

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            item = self._items[index.row()]
            match index.column():
                case 0:
                    return item.name
                case 1:
                    return item.unit
                case 2:
                    return item.description

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parent: QModelIndex = ...):
        return len(self._items)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.header)
