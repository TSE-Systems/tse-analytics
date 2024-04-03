from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.meal_details.data.meal_details import MealDetails


class MealDetailsTreeItem(TreeItem):
    def __init__(self, meal_details: MealDetails):
        super().__init__(meal_details.name)

        self.meal_details = meal_details

    @property
    def icon(self):
        return QIcon(":/icons/icons8-details-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.meal_details.name
