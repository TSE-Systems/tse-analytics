from PySide6.QtWidgets import QComboBox, QWidget

from tse_analytics.core.data.shared import Factor, FactorRole


class FactorSelector(QComboBox):
    """
    A combo box widget for selecting a factor from a list.

    This widget displays a dropdown list of available factors,
    allowing the user to select one factor for analysis.
    """

    def __init__(
        self,
        parent: QWidget,
        factors: dict[str, Factor],
        selected_factor: str = None,
        show_role: FactorRole | None = None,
    ):
        super().__init__(parent)

        self.clear()
        if show_role is None:
            items = list(factors)
        else:
            items = [factor.name for factor in factors.values() if factor.role == show_role]
        self.addItems(items)
        if selected_factor is not None:
            self.setCurrentText(selected_factor)
