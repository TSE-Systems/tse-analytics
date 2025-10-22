from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from tse_analytics.core.data.shared import Factor


class FactorsTableWidget(QTableWidget):
    """
    A table widget for displaying and selecting factors.

    This widget presents factors and their levels in a table format,
    allowing users to view and select factors for analysis.
    """

    _COLUMN_NUMBER = 2

    def __init__(self, parent=None):
        """
        Initialize the FactorsTableWidget.

        Args:
            parent: The parent widget. Default is None.
        """
        super().__init__(parent)

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSortingEnabled(True)
        self.setColumnCount(self._COLUMN_NUMBER)
        self.setHorizontalHeaderLabels(["Name", "Levels"])
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setMinimumSectionSize(20)
        self.verticalHeader().setDefaultSectionSize(20)

        pal = self.palette()
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.Highlight,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight),
        )
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.HighlightedText,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText),
        )
        self.setPalette(pal)

    def set_selection_mode(self, mode: QAbstractItemView.SelectionMode) -> None:
        """
        Set the selection mode for the table.

        Args:
            mode: The selection mode to use (e.g., SingleSelection, MultiSelection).
        """
        self.setSelectionMode(mode)

    def set_data(self, factors: dict[str, Factor], selected_factors: list[str] = None) -> None:
        """
        Populate the table with factor data.

        This method clears any existing data and fills the table with the provided factors,
        displaying their names and levels.
        """
        self.setRowCount(len(factors))
        for i, factor in enumerate(factors.values()):
            self.setItem(i, 0, QTableWidgetItem(factor.name))
            level_names = [level.name for level in factor.levels]
            self.setItem(i, 1, QTableWidgetItem(f"{', '.join(level_names)}"))
            if selected_factors is not None:
                if factor.name in selected_factors:
                    self.selectRow(i)

    def clear_data(self) -> None:
        """
        Clear all data from the table.

        This method removes all rows from the table, effectively clearing all factor data.
        """
        self.setRowCount(0)

    def get_selected_factor_names(self) -> list[str]:
        """
        Get the names of all currently selected factors.

        Returns:
            A list of factor names that are currently selected in the table.
        """
        selected_items = self.selectedItems()
        result = []
        for i in range(0, len(selected_items) // self._COLUMN_NUMBER):
            result.append(selected_items[i * self._COLUMN_NUMBER].text())
        return result
