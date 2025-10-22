import weakref


class TreeItem:
    """
    Base class for items in a tree structure.

    This class provides the foundation for building hierarchical tree structures
    with parent-child relationships. It supports properties like name, icon,
    foreground color, tooltip, and checked state.
    """

    def __init__(self, name: str, parent=None, color: str | None = None):
        """
        Initialize a tree item with the given name and optional parent.

        Args:
            name (str): The display name of the tree item.
            parent (TreeItem, optional): The parent tree item. Defaults to None.
        """
        self.name = name
        self.color = color
        self.parent_item = weakref.ref(parent) if parent else None
        self.child_items: list[TreeItem] = []
        self._checked = False

    @property
    def icon(self):
        """
        Get the icon to display for this item in the tree view.

        Returns:
            QIcon or None: The icon for this item. None by default.
        """
        return None

    @property
    def foreground(self):
        """
        Get the foreground color for this item in the tree view.

        Returns:
            QBrush or None: The brush for the text color. None by default.
        """
        return None

    @property
    def tooltip(self) -> str | None:
        """
        Get the tooltip text for this item in the tree view.

        Returns:
            str or None: The tooltip text. None by default.
        """
        return None

    def child_count(self) -> int:
        """
        Get the number of child items.

        Returns:
            int: The number of children.
        """
        return len(self.child_items)

    def child(self, row: int):
        """
        Get the child item at the specified row.

        Args:
            row (int): The row index of the child.

        Returns:
            TreeItem or None: The child item at the specified row,
                             or None if the row is out of range.
        """
        return self.child_items[row] if 0 <= row < len(self.child_items) else None

    def parent(self):
        """
        Get the parent item.

        Returns:
            TreeItem or None: The parent item, or None if this is a root item.
        """
        return self.parent_item() if self.parent_item else None

    def row(self) -> int:
        """
        Get the row index of this item within its parent's children.

        Returns:
            int: The row index, or 0 if this is a root item.
        """
        if self.parent_item:
            return self.parent_item().child_items.index(self)
        return 0

    def add_child(self, child):
        """
        Add a child item to this item.

        Args:
            child (TreeItem): The child item to add.
        """
        child.parent_item = weakref.ref(self)
        self.child_items.append(child)

    def clear(self):
        """
        Remove all child items from this item.
        """
        # for child in self.child_items:
        #     child.parent_item = None
        self.child_items.clear()

    def data(self, column: int):
        """
        Get the data for the specified column.

        Args:
            column (int): The column index.

        Returns:
            str: The name of this item (regardless of column).
        """
        return self.name

    @property
    def checked(self):
        """
        Get the checked state of this item.

        Returns:
            bool: True if the item is checked, False otherwise.
        """
        return self._checked

    @checked.setter
    def checked(self, state: bool):
        """
        Set the checked state of this item.

        Args:
            state (bool): The new checked state.
        """
        self._checked = bool(state)
