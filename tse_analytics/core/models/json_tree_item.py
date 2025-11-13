from __future__ import annotations


class TreeItem:
    """
    A tree item representing a node in a JSON data structure.

    This class provides the foundation for building a hierarchical representation
    of JSON data, with each item storing a key-value pair and maintaining
    parent-child relationships. It is used by JsonModel to display and edit
    JSON data in a tree view.
    """

    def __init__(self, parent: TreeItem | None = None):
        """
        Initialize a tree item with the given parent.

        Args:
            parent (TreeItem, optional): The parent tree item. Defaults to None.
        """
        self._parent = parent
        self._key: str | int = ""
        self._value = ""
        self._value_type = None
        self._children: list[TreeItem] = []

    def appendChild(self, item: TreeItem):
        """Add item as a child"""
        self._children.append(item)

    def child(self, row: int) -> TreeItem:
        """Return the child of the current item from the given row"""
        return self._children[row]

    def parent(self) -> TreeItem | None:
        """Return the parent of the current item"""
        return self._parent

    def childCount(self):
        """Return the number of children of the current item"""
        return len(self._children)

    def row(self):
        """Return the row where the current item occupies in the parent"""
        return self._parent._children.index(self) if self._parent else 0

    @property
    def key(self):
        """Return the key name"""
        return self._key

    @key.setter
    def key(self, key: str):
        """Set key name of the current item"""
        self._key = key

    @property
    def value(self):
        """Return the value name of the current item"""
        return self._value

    @value.setter
    def value(self, value: str):
        """Set value name of the current item"""
        self._value = value

    @property
    def value_type(self):
        """Return the python type of the item's value."""
        return self._value_type

    @value_type.setter
    def value_type(self, value):
        """Set the python type of the item's value."""
        self._value_type = value

    @classmethod
    def load(cls, value: list | dict, parent: TreeItem | None = None, sort=True) -> TreeItem:
        """
        Create a tree structure from a nested list or dictionary.

        This method recursively processes JSON-compatible data structures and
        builds a corresponding tree of TreeItem objects. For dictionaries,
        each key-value pair becomes a child item. For lists, each element
        becomes a child item with its index as the key.

        Args:
            value (list | dict): The JSON-compatible data to convert to a tree.
            parent (TreeItem, optional): The parent item for the new tree.
                                        Defaults to None.
            sort (bool, optional): Whether to sort dictionary keys alphabetically.
                                  Defaults to True.

        Examples:
            with open("file.json") as file:
                data = json.load(file)
                root = TreeItem.load(data)

        Returns:
            TreeItem: The root item of the created tree structure.
        """
        rootItem = TreeItem(parent)
        rootItem.key = "root"

        if isinstance(value, dict):
            items = sorted(value.items()) if sort else value.items()

            for key, value in items:
                child = cls.load(value, rootItem)
                child.key = key
                child.value_type = type(value)
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for index, val in enumerate(value):
                child = cls.load(val, rootItem)
                child.key = index
                child.value_type = type(val)
                rootItem.appendChild(child)

        else:
            rootItem.value = value
            rootItem.value_type = type(value)

        return rootItem
