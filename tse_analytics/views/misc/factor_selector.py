from PySide6.QtWidgets import QComboBox

from tse_analytics.core.data.shared import Factor


class FactorSelector(QComboBox):
    """
    A combo box widget for selecting a factor from a list.

    This widget displays a dropdown list of available factors,
    allowing the user to select one factor for analysis.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def set_data(self, factors: dict[str, Factor], selected_factor: str = None) -> None:
        self.clear()
        items = list(factors)
        self.addItems(items)
        if selected_factor is not None:
            self.setCurrentText(selected_factor)
