import weakref

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.submodules.actimot.data.actimot_data import ActimotData


class ActimotTreeItem(TreeItem):
    def __init__(self, actimot_data: ActimotData):
        super().__init__(actimot_data.name)

        self._actimot_data = weakref.ref(actimot_data)

    @property
    def actimot_data(self):
        return self._actimot_data()

    @property
    def dataset(self):
        return self.actimot_data.dataset

    @property
    def icon(self):
        return QIcon(":/icons/icons8-extension-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.actimot_data.name
