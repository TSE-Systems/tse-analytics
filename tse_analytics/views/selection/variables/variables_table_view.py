from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QHeaderView, QTableView

from tse_analytics.core.manager import Manager
from tse_analytics.models.variables_model import VariablesModel
from tse_datatools.data.variable import Variable


class VariablesTableView(QTableView):
    def __init__(self, parent):
        super().__init__(parent)

        pal = self.palette()
        pal.setColor(QPalette.Inactive, QPalette.Highlight, pal.color(QPalette.Active, QPalette.Highlight))
        pal.setColor(QPalette.Inactive, QPalette.HighlightedText, pal.color(QPalette.Active, QPalette.HighlightedText))
        self.setPalette(pal)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setModel(proxy_model)
        self.horizontalHeader().ResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().setDefaultSectionSize(10)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setSortingEnabled(True)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def clear(self):
        self.model().setSourceModel(None)

    def set_data(self, variables: dict[str, Variable]):
        model = VariablesModel(list(variables.values()))
        self.model().setSourceModel(model)

    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model: QSortFilterProxyModel = self.model()
        model = proxy_model.sourceModel()
        selected_variables: list[Variable] = []
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                variable = model.items[row]
                selected_variables.append(variable)
        Manager.data.set_selected_variables(selected_variables)
