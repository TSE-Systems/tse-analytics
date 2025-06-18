import weakref

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QIcon

from tse_analytics.core.models.tree_item import TreeItem


class DatasetTreeItem(TreeItem):
    """
    A tree item representing a dataset in a tree view.

    This class extends TreeItem to represent a dataset object in a tree structure,
    providing access to the dataset and its visual representation properties.
    """
    def __init__(self, dataset):
        """
        Initialize a dataset tree item with the given dataset.

        Args:
            dataset: The dataset object to represent in the tree.
        """
        super().__init__(dataset.name)

        self._dataset = weakref.ref(dataset)

    @property
    def dataset(self):
        """
        Get the dataset object associated with this tree item.

        Returns:
            The dataset object referenced by this tree item.
        """
        return self._dataset()

    @property
    def icon(self):
        """
        Get the icon to display for this dataset in the tree view.

        Returns:
            QIcon: An icon representing a dataset.
        """
        return QIcon(":/icons/icons8-sheets-16.png")

    @property
    def foreground(self):
        """
        Get the foreground color for this dataset in the tree view.

        Returns:
            QBrush: A brush with black color for the text.
        """
        return QBrush(Qt.GlobalColor.black)

    @property
    def tooltip(self):
        """
        Get the tooltip text for this dataset in the tree view.

        Returns:
            str: The description of the dataset.
        """
        return self.dataset.description
