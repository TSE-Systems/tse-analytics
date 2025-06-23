import weakref

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem


class ExtensionTreeItem(TreeItem):
    """
    A tree item representing an extension in a tree view.

    This class extends TreeItem to represent an extension object in a tree structure,
    providing access to the extension data and its visual representation properties.
    """

    def __init__(self, extension_data):
        """
        Initialize an extension tree item with the given extension data.

        Args:
            extension_data: The extension data object to represent in the tree.
        """
        super().__init__(extension_data.name)

        self._extension_data = weakref.ref(extension_data)

    @property
    def extension_data(self):
        """
        Get the extension data object associated with this tree item.

        Returns:
            The extension data object referenced by this tree item.
        """
        return self._extension_data()

    @property
    def icon(self):
        """
        Get the icon to display for this extension in the tree view.

        Returns:
            QIcon: An icon representing an extension.
        """
        return QIcon(":/icons/icons8-extension-16.png")

    @property
    def foreground(self):
        """
        Get the foreground color for this extension in the tree view.

        Returns:
            QBrush: A brush with black color for the text.
        """
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        """
        Get the tooltip text for this extension in the tree view.

        Returns:
            str: The name of the extension.
        """
        return self.extension_data.name
