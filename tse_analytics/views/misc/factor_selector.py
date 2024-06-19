from PySide6.QtWidgets import QComboBox

from tse_analytics.core.data.shared import Factor


class FactorSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def set_data(self, factors: dict[str, Factor], add_empty_item=True):
        self.clear()
        items = [""] + list(factors.keys()) if add_empty_item else list(factors.keys())
        self.addItems(items)
