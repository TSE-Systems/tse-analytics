from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.intellimaze.animalgate.data.animalgate_data import AnimalGateData


class AnimalGateTreeItem(TreeItem):
    def __init__(self, animalgate_data: AnimalGateData):
        super().__init__(animalgate_data.name)

        self.animalgate_data = animalgate_data

    @property
    def icon(self):
        return QIcon(":/icons/icons8-details-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.animalgate_data.name
