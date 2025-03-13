from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_data import CaloData


class CaloDataTreeItem(TreeItem):
    def __init__(self, calo_data: CaloData):
        super().__init__(calo_data.name)

        self.calo_data = calo_data

    @property
    def icon(self):
        return QIcon(":/icons/icons8-extension-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.calo_data.name
