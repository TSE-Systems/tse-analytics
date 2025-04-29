import weakref


class TreeItem:
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent_item = weakref.ref(parent) if parent else None
        self.child_items = []
        self._checked = False

    @property
    def icon(self):
        return None

    @property
    def foreground(self):
        return None

    @property
    def tooltip(self) -> str | None:
        return None

    def child_count(self) -> int:
        return len(self.child_items)

    def child(self, row: int):
        return self.child_items[row] if 0 <= row < len(self.child_items) else None

    def parent(self):
        return self.parent_item() if self.parent_item else None

    def row(self) -> int:
        if self.parent_item:
            return self.parent_item().child_items.index(self)
        return 0

    def add_child(self, child):
        child.parent_item = weakref.ref(self)
        self.child_items.append(child)

    def clear(self):
        # for child in self.child_items:
        #     child.parent_item = None
        self.child_items.clear()

    def data(self, column: int):
        return self.name

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, state: bool):
        self._checked = bool(state)
