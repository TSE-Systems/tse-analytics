import weakref

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.models.tree_item import TreeItem


class DatatableTreeItem(TreeItem):
    """
    A tree item representing a datatable in a tree view.

    This class extends TreeItem to represent a datatable object in a tree structure,
    providing access to the datatable and its visual representation properties.
    """

    def __init__(self, datatable: Datatable):
        """
        Initialize a datatable tree item with the given datatable.

        Args:
            datatable (Datatable): The datatable object to represent in the tree.
        """
        super().__init__(datatable.name)

        self._datatable = weakref.ref(datatable)

    @property
    def datatable(self):
        """
        Get the datatable object associated with this tree item.

        Returns:
            Datatable: The datatable object referenced by this tree item.
        """
        return self._datatable()

    @property
    def dataset(self):
        return self.datatable.dataset

    @property
    def icon(self):
        """
        Get the icon to display for this datatable in the tree view.

        Returns:
            QIcon: An icon representing a datatable.
        """
        return QIcon(":/icons/icons8-data-sheet-16.png")

    @property
    def foreground(self):
        """
        Get the foreground color for this datatable in the tree view.

        Returns:
            QBrush: A brush with black color for the text.
        """
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        """
        Get the tooltip text for this datatable in the tree view.

        Returns:
            str: The description of the datatable.
        """
        return self.datatable.description
