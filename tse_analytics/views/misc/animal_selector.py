from PySide6.QtWidgets import QComboBox

from tse_analytics.core.data.shared import Animal


class AnimalSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def set_data(self, animals: dict[str, Animal], add_empty_item=True):
        self.clear()
        items = [""] + list(animals.keys()) if add_empty_item else list(animals.keys())
        self.addItems(items)
