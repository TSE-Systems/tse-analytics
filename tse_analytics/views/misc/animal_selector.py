from PySide6.QtWidgets import QComboBox

from tse_analytics.core.data.shared import Animal


class AnimalSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.animals: dict[str, Animal] = {}

    def set_data(self, animals: dict[str, Animal], add_empty_item=False):
        self.animals = animals
        self.clear()
        items = [""] + list(animals) if add_empty_item else list(animals)
        self.addItems(items)

    def get_selected_animal(self) -> Animal | None:
        animal_name = self.currentText()
        return self.animals[animal_name] if animal_name != "" else None
