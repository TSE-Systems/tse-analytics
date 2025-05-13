from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from tse_analytics.core.data.dataset import Dataset


class AnimalsSimpleModel(QAbstractTableModel):
    def __init__(self, dataset: Dataset, parent=None):
        super().__init__(parent)

        self.dataset = dataset
        self.items = list(dataset.animals.values())

        self.header = ["Animal"]
        if len(self.items) > 0:
            properties_header = list(self.items[0].properties.keys())
            self.header = self.header + properties_header

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        item = self.items[index.row()]
        match index.column():
            case 0:
                if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                    return item.id
                elif role == Qt.ItemDataRole.DecorationRole:
                    return QColor(item.color)
                elif role == Qt.ItemDataRole.CheckStateRole:
                    return Qt.CheckState.Checked if item.enabled else Qt.CheckState.Unchecked
            case _:
                if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                    return item.properties[self.header[index.column()]]

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parent: QModelIndex = ...):
        return len(self.items)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self.header)
