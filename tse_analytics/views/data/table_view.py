import pandas as pd
from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QHeaderView, QTableView, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.models.pandas_model import PandasModel


class TableView(QTableView):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setModel(proxy_model)
        self.horizontalHeader().ResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().setDefaultSectionSize(10)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        self._sorting: bool = False

    def set_data(self, df: pd.DataFrame):
        selected_variable_names = [item.name for item in Manager.data.selected_variables]
        selected_variable_names = set(selected_variable_names)

        all_variable_names = Manager.data.selected_dataset.variables
        all_variable_names = set(all_variable_names)

        drop_columns = all_variable_names - selected_variable_names

        df = df.drop(columns=drop_columns)

        model = PandasModel(df)
        self.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self.setSortingEnabled(False)
        self.model().setSourceModel(model)
        self.setSortingEnabled(self._sorting)

    def clear(self):
        self.model().setSourceModel(None)

    def set_sorting(self, state: bool):
        self._sorting = state
        self.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self.setSortingEnabled(self._sorting)

    def resize_columns_width(self):
        self.resizeColumnsToContents()
