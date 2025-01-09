from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class IMDevicesModel(QAbstractTableModel):
    def __init__(self, device_ids: list[str], header: list[str], parent=None):
        super().__init__(parent)

        self.items = device_ids
        self.header = header

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            item = self.items[index.row()]
            return item

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)
