import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from tse_analytics.modules.phenomaster.meal_details.data.meal_details_animal_item import MealDetailsAnimalItem


class MealDetailsBoxesModel(QAbstractTableModel):
    def __init__(self, items: list[MealDetailsAnimalItem], header: list[str], parent=None):
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
                case 2:
                    return item.diet
                case _:
                    return item.factors[self.header[column]]

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
