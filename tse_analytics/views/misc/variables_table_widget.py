from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem

from tse_analytics.core.data.shared import Variable


class VariablesTableWidget(QTableWidget):
    _COLUMN_NUMBER = 3

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSortingEnabled(True)
        self.setColumnCount(self._COLUMN_NUMBER)
        self.setHorizontalHeaderLabels(["Name", "Unit", "Description"])
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

        self.variables: dict[str, Variable] = {}

    def set_data(self, variables: dict[str, Variable]) -> None:
        self.variables = variables
        self.setRowCount(len(variables))
        for i, variable in enumerate(variables.values()):
            self.setItem(i, 0, QTableWidgetItem(variable.name))
            self.setItem(i, 1, QTableWidgetItem(variable.unit))
            self.setItem(i, 2, QTableWidgetItem(variable.description))
        self.resizeColumnsToContents()

    def clear_data(self) -> None:
        self.setRowCount(0)

    def get_selected_variable_names(self) -> list[str]:
        selected_items = self.selectedItems()
        result = []
        for i in range(0, len(selected_items) // self._COLUMN_NUMBER):
            result.append(selected_items[i * self._COLUMN_NUMBER].text())
        return result

    def get_selected_variables_dict(self) -> dict[str, Variable]:
        selected_items = self.selectedItems()
        result = {}
        for i in range(0, len(selected_items) // self._COLUMN_NUMBER):
            var_name = selected_items[i * self._COLUMN_NUMBER].text()
            result[var_name] = self.variables[var_name]
        return result
