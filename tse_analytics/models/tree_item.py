from typing import Optional

from PySide6.QtCore import Qt


class TreeItem:
    column_names = ["Name"]
    column_flags = [Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable]

    def __init__(self, name: str, meta: Optional[dict] = None):
        self.name = name
        self.meta: Optional[dict] = meta
        self.parent_item = None
        self.child_items = []
        self._row = 0
        self._checked = False

    @property
    def icon(self):
        return None

    @property
    def foreground(self):
        return None

    @property
    def tooltip(self):
        return None

    @property
    def column_data(self):
        return [self.name]

    def column_count(self):
        return len(self.column_names)

    def child_count(self):
        return len(self.child_items)

    def child(self, row: int):
        if 0 <= row < self.child_count():
            return self.child_items[row]

    def parent(self):
        return self.parent_item

    def row(self):
        return self._row

    def add_child(self, child):
        child.parent_item = self
        child._row = len(self.child_items)
        self.child_items.append(child)

    def remove_child(self, position: int):
        if position < 0 or position > self.child_count():
            return False
        child = self.child_items.pop(position)
        child.parent_item = None
        return True

    def clear(self):
        self.child_items.clear()

    def data(self, column: int):
        if 0 <= column < self.column_count():
            return self.column_data[column]

    def set_data(self, column: int, value):
        if column == 0:
            self.checked = value
            return True
        return False

    def flags(self, column: int):
        return self.column_flags[column]

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, state: bool):
        self._checked = bool(state)
