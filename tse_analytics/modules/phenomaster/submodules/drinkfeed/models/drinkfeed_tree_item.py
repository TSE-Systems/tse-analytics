import weakref

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_data import DrinkFeedData


class DrinkFeedTreeItem(TreeItem):
    def __init__(self, drinkfeed_data: DrinkFeedData):
        super().__init__(drinkfeed_data.name)

        self._drinkfeed_data = weakref.ref(drinkfeed_data)

    @property
    def drinkfeed_data(self):
        return self._drinkfeed_data()

    @property
    def icon(self):
        return QIcon(":/icons/icons8-extension-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.drinkfeed_data.name
