from PySide6.QtWidgets import QComboBox
from tse_datatools.data.factor import Factor


class FactorSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def set_data(self, factors: dict[str, Factor]):
        items = [""] + list(factors.keys())
        self.addItems(items)
