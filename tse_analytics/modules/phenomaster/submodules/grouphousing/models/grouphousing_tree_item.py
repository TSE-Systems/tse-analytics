import weakref

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.submodules.grouphousing.data.grouphousing_data import GroupHousingData


class GroupHousingTreeItem(TreeItem):
    def __init__(self, grouphousing_data: GroupHousingData):
        super().__init__(grouphousing_data.name)

        self._grouphousing_data = weakref.ref(grouphousing_data)

    @property
    def grouphousing_data(self):
        return self._grouphousing_data()

    @property
    def icon(self):
        return QIcon(":/icons/icons8-extension-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.grouphousing_data.name
