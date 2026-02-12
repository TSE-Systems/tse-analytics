from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QHeaderView, QTableView

from tse_analytics.core.data.shared import Variable
from tse_analytics.core.models.variables_simple_model import VariablesSimpleModel


class VariableSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table_view = QTableView(
            self,
            sortingEnabled=False,
        )
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setAutoScroll(False)
        self.table_view.horizontalHeader().ResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.verticalHeader().hide()
        self.table_view.verticalHeader().setDefaultSectionSize(20)

        self.setView(self.table_view)

        self.variables: dict[str, Variable] = {}

    def set_data(self, variables: dict[str, Variable], selected_variable: str | None = None) -> None:
        self.variables = variables
        model = VariablesSimpleModel(list(variables.values()))
        self.setModel(model)
        self.table_view.resizeColumnsToContents()
        self.table_view.resizeRowsToContents()
        self.table_view.setMinimumWidth(self.table_view.horizontalHeader().length())
        if selected_variable is not None:
            self.setCurrentText(selected_variable)

    def get_selected_variable(self) -> Variable | None:
        var_name = self.currentText()
        return self.variables[var_name] if var_name != "" else None
