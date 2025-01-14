from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem


class ExtensionTreeItem(TreeItem):
    def __init__(self, extension_data):
        super().__init__(extension_data.name)

        self.extension_data = extension_data

    @property
    def icon(self):
        return QIcon(":/icons/icons8-extension-16.png")

    @property
    def foreground(self):
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        return self.extension_data.name
