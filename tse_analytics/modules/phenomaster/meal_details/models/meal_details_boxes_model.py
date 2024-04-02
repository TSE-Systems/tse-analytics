import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.modules.phenomaster.meal_details.data.meal_details_box import MealDetailsBox


class MealDetailsBoxesModel(QAbstractTableModel):
    header = ["Box", "Animal", "Diet"]

    def __init__(self, items: list[MealDetailsBox], parent=None):
        super().__init__(parent)

        self.items = items

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            item = self.items[index.row()]
            match index.column():
                case 0:
                    return item.box
                case 1:
                    return item.animal
                case 2:
                    return item.diet

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.header[col]

    def rowCount(self, parent):
        return len(self.items)

    def columnCount(self, parent):
        return len(self.header)

    def clear_diets(self, indexes: list[QModelIndex]):
        rows = {index.row() for index in indexes}
        for row in rows:
            self.items[row].diet = pd.NA

    def set_diet(self, indexes: list[QModelIndex], diet: float):
        rows = {index.row() for index in indexes}
        for row in rows:
            self.items[row].diet = diet

    def get_diets_dict(self):
        return {item.box: item.diet for item in self.items}
