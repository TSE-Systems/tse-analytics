from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from tse_analytics.core.data.shared import Factor


class FactorsTableWidget(QTableWidget):
    _COLUMN_NUMBER = 2

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSortingEnabled(True)
        self.setColumnCount(self._COLUMN_NUMBER)
        self.setHorizontalHeaderLabels(["Name", "Groups"])
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
        self.setSelectionMode(mode)

    def set_data(self, factors: dict[str, Factor]) -> None:
        self.setRowCount(len(factors))
        for i, factor in enumerate(factors.values()):
            self.setItem(i, 0, QTableWidgetItem(factor.name))
            group_names = [group.name for group in factor.groups]
            self.setItem(i, 1, QTableWidgetItem(f"{', '.join(group_names)}"))

    def clear_data(self) -> None:
        self.setRowCount(0)

    def get_selected_factor_names(self) -> list[str]:
        selected_items = self.selectedItems()
        result = []
        for i in range(0, len(selected_items) // self._COLUMN_NUMBER):
            result.append(selected_items[i * self._COLUMN_NUMBER].text())
        return result
