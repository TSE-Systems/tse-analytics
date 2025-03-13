from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.models.tree_item import TreeItem


class DatatableTreeItem(TreeItem):
    def __init__(self, datatable: Datatable):
        super().__init__(datatable.name)

        self.datatable = datatable

    @property
    def icon(self):
        return QIcon(":/icons/icons8-data-sheet-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.datatable.description
