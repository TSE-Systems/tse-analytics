from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.modules.phenomaster.submodules.grouphousing.data.grouphousing_animal_item import (
    GroupHousingAnimalItem,
)


class GroupHousingBoxesModel(QAbstractTableModel):
    def __init__(self, items: list[GroupHousingAnimalItem], header: list[str], parent=None):
        super().__init__(parent)

        self.items = items
        self.header = header

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            item = self.items[index.row()]
            column = index.column()
            match column:
                case 0:
                    return item.animal
                case 1:
                    return item.box
                case _:
                    return item.factors[self.header[column]]

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)
