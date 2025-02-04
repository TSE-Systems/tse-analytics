from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.trafficage.data.trafficage_data import TraffiCageData


class TraffiCageTreeItem(TreeItem):
    def __init__(self, trafficage_data: TraffiCageData):
        super().__init__(trafficage_data.name)

        self.trafficage_data = trafficage_data

    @property
    def icon(self):
        return QIcon(":/icons/icons8-details-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.trafficage_data.name
