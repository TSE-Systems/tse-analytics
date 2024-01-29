from collections.abc import Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from tse_datatools.data.variable import Variable


class VariablesModel(QAbstractTableModel):
    header = ("Name", "Unit", "Description")

    def __init__(self, items: Sequence[Variable], parent=None):
        super().__init__(parent)

        self.items = items

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if not index.isValid():
            return None
        elif role != Qt.ItemDataRole.DisplayRole:
            return None
        item = self.items[index.row()]
        values = (item.name, item.unit, item.description)
        return values[index.column()]

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)
