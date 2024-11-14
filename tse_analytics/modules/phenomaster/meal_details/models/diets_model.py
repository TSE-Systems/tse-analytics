from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.core.data.shared import AnimalDiet


class DietsModel(QAbstractTableModel):
    header = ("Name", "Caloric Value [kcal/g]")

    def __init__(self, items: list[AnimalDiet], parent=None):
        super().__init__(parent)
        self.items = items

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            item = self.items[index.row()]
            values = (item.name, item.caloric_value)
            return values[index.column()]

    def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.EditRole:
            item = self.items[index.row()]
            if index.column() == 0:
                item.name = value
            elif index.column() == 1:
                try:
                    item.caloric_value = float(value)
                except ValueError:
                    return False
            else:
                return False
            return True

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)

    def flags(self, index: QModelIndex):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def add_diet(self, diet: AnimalDiet):
        self.items.append(diet)
        # Trigger refresh.
        self.layoutChanged.emit()

    def delete_diet(self, index):
        # Remove the item and refresh.
        del self.items[index.row()]
        self.layoutChanged.emit()
