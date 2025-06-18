from PySide6.QtWidgets import QComboBox

from tse_analytics.core.data.shared import Factor


class FactorSelector(QComboBox):
    """
    A combo box widget for selecting a factor from a list.

    This widget displays a dropdown list of available factors,
    allowing the user to select one factor for analysis.
    """

    def __init__(self, parent=None):
        """
        Initialize the FactorSelector widget.

        Args:
            parent: The parent widget. Default is None.
        """
        super().__init__(parent)

    def set_data(self, factors: dict[str, Factor], add_empty_item=True):
        """
        Populate the combo box with factor names.

        This method clears any existing items and adds the names of the provided factors.

        Args:
            factors: Dictionary mapping factor names to Factor objects.
            add_empty_item: If True, adds an empty item at the beginning of the list.
                           Default is True.
        """
        self.clear()
        items = [""] + list(factors.keys()) if add_empty_item else list(factors.keys())
        self.addItems(items)
