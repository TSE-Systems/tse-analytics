from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QBrush
from tse_datatools.data.dataset import Dataset

from tse_analytics.models.actimot_tree_item import ActiMotTreeItem
from tse_analytics.models.calorimetry_tree_item import CalorimetryTreeItem
from tse_analytics.models.tree_item import TreeItem
from tse_analytics.models.drinkfeed_tree_item import DrinkFeedTreeItem


class DatasetTreeItem(TreeItem):
    def __init__(self, dataset: Dataset):
        super().__init__(dataset.name)

        self.dataset = dataset

    @property
    def loaded(self) -> bool:
        return self.dataset.loaded

    @property
    def icon(self):
        return QIcon(":/icons/icons8-sheets-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.black) if self.loaded else QBrush(Qt.gray)

    @property
    def tooltip(self):
        return "DatasetTreeItem"

    def load(self):
        if self.loaded:
            return
        self.dataset.load(extract_groups=False)
        if self.dataset.meta:
            self.meta = self.dataset.meta
        if self.dataset.calorimetry is not None:
            self.add_child(CalorimetryTreeItem(self.dataset.calorimetry))
        if self.dataset.actimot is not None:
            self.add_child(ActiMotTreeItem(self.dataset.actimot))
        if self.dataset.drinkfeed is not None:
            self.add_child(DrinkFeedTreeItem(self.dataset.drinkfeed))

    def close(self):
        if not self.loaded:
            return
        self.dataset.unload()
        self.clear()
