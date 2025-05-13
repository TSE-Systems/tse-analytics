from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class BinsModel(QAbstractTableModel):
    header = ["Bin"]

    def __init__(self, items: list[int], parent=None):
        super().__init__(parent)

        self.items = items

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            item = self.items[index.row()]
            return int(item)

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.items)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.header)
