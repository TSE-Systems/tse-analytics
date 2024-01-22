from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QTableView, QHeaderView

from tse_analytics.models.variables_model import VariablesModel
from tse_datatools.data.variable import Variable


class VariableSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table_view = QTableView(self)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setAutoScroll(False)
        self.table_view.setSortingEnabled(False)
        self.table_view.horizontalHeader().ResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.verticalHeader().hide()
        self.table_view.verticalHeader().setDefaultSectionSize(20)

        self.setView(self.table_view)

    def set_data(self, variables: dict[str, Variable]):
        model = VariablesModel(list(variables.values()))
        self.setModel(model)
        self.table_view.resizeColumnsToContents()
        self.table_view.resizeRowsToContents()
        self.table_view.setMinimumWidth(self.table_view.horizontalHeader().length())
