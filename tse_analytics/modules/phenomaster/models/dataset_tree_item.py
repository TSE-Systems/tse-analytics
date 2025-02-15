from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.data.dataset import Dataset


class DatasetTreeItem(TreeItem):
    def __init__(self, dataset: Dataset):
        super().__init__(dataset.name)

        self.dataset = dataset
        self.meta = dataset.meta

    @property
    def icon(self):
        return QIcon(":/icons/icons8-sheets-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.dataset.name
