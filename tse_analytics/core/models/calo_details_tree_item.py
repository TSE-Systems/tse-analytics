from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.data.calo_details import CaloDetails


class CaloDetailsTreeItem(TreeItem):
    def __init__(self, calo_details: CaloDetails):
        super().__init__(calo_details.name)

        self.calo_details = calo_details

    @property
    def icon(self):
        return QIcon(":/icons/icons8-details-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.calo_details.name
