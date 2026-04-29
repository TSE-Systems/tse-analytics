from PySide6.QtWidgets import QAbstractItemView, QAbstractScrollArea, QTableWidget, QTableWidgetItem

from tse_analytics.core.data.shared import Factor, FactorRole
from tse_analytics.core.utils.ui import set_inactive_palette


class FactorsTableWidget(QTableWidget):
    """
    A table widget for displaying and selecting factors.

    This widget presents factors and their levels in a table format,
    allowing users to view and select factors for analysis.
    """

    _COLUMN_NUMBER = 2

    def __init__(
        self,
        factors: dict[str, Factor],
        selected_factors: list[str],
        show_role: FactorRole | None,
        show_bins: int | None = None,
        parent=None,
    ):
        if show_role is not None:
            factors = {name: factor for name, factor in factors.items() if factor.role == show_role}

        super().__init__(
            parent,
            rowCount=len(factors) + 1 if show_bins else len(factors),
            columnCount=self._COLUMN_NUMBER,
        )

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setSortingEnabled(True)
        self.setHorizontalHeaderLabels(["Name", "Levels"])
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setMinimumSectionSize(20)
        self.verticalHeader().setDefaultSectionSize(20)

        set_inactive_palette(self)

        for i, factor in enumerate(factors.values()):
            self.setItem(i, 0, QTableWidgetItem(factor.name))
            level_names = [level.name for level in factor.levels]
            self.setItem(i, 1, QTableWidgetItem(f"{', '.join(level_names)}"))
            if selected_factors is not None:
                if factor.name in selected_factors:
                    self.selectRow(i)

        if show_bins:
            self.setItem(len(factors), 0, QTableWidgetItem("Bin"))
            self.setItem(len(factors), 1, QTableWidgetItem(f"Bins: {show_bins}"))

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
