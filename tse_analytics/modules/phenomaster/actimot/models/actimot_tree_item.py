from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem
from tse_analytics.modules.phenomaster.actimot.data.actimot_details import ActimotDetails


class ActimotTreeItem(TreeItem):
    def __init__(self, actimot_details: ActimotDetails):
        super().__init__(actimot_details.name)

        self.actimot_details = actimot_details

    @property
    def icon(self):
        return QIcon(":/icons/icons8-details-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.actimot_details.name
