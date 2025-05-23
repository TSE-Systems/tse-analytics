from __future__ import annotations


class TreeItem:
    """A Json item corresponding to a line in QTreeView"""

    def __init__(self, parent: TreeItem | None = None):
        self._parent = parent
        self._key = ""
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
        """Create a 'root' TreeItem from a nested list or a nested dictonary

        Examples:
            with open("file.json") as file:
                data = json.dump(file)
                root = TreeItem.load(data)

        This method is a recursive function that calls itself.

        Returns:
            TreeItem: TreeItem
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
