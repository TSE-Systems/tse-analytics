from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QBrush
from tse_datatools.data.dataset import Dataset

from tse_analytics.models.tree_item import TreeItem


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
        return QBrush(Qt.black)

    @property
    def tooltip(self):
        return "DatasetTreeItem"
