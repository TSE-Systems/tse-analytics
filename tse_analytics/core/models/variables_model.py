from collections.abc import Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.core.data.shared import Variable


class VariablesModel(QAbstractTableModel):
    header = ("Name", "Unit", "Aggregation", "Outliers", "Description")

    def __init__(self, items: Sequence[Variable], parent=None):
        super().__init__(parent)

        self.items = items

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        item = self.items[index.row()]
        match index.column():
            case 0:
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.name
            case 1:
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.unit
            case 2:
                if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                    return item.aggregation
            case 3:
                if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.CheckStateRole:
                    return Qt.CheckState.Checked if item.outliers else Qt.CheckState.Unchecked
            case 4:
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.description

    def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole):
        match index.column():
            case 2:
                if role == Qt.ItemDataRole.EditRole:
                    item = self.items[index.row()]
                    item.aggregation = value
                    # Manager.data.rename_animal(old_id, item)
                    return True
            case 3:
                if role == Qt.ItemDataRole.CheckStateRole:
                    item = self.items[index.row()]
                    item.outliers = value == Qt.CheckState.Checked.value
                    # Manager.data.set_selected_animals()
                    return True

    def flags(self, index: QModelIndex):
        match index.column():
            case 2:
                return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
            case 3:
                return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable
            case _:
                return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]
        return None

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)
