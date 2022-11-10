from typing import Optional

import pandas as pd
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QWidget, QTableView, QHeaderView

from tse_analytics.models.pandas_model import PandasModel
from tse_datatools.data.animal import Animal


class TableView(QTableView):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setModel(proxy_model)
        self.horizontalHeader().ResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setDefaultSectionSize(10)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setEditTriggers(QTableView.NoEditTriggers)

        self._sorting: bool = False
        self._df: Optional[pd.DataFrame] = None

    def set_data(self, df: pd.DataFrame):
        self._df = df
        self._set_source_model(df)

    def filter_animals(self, animals: list[Animal]):
        animal_ids = [animal.id for animal in animals]
        df = self._df
        df = df[df['Animal'].isin(animal_ids)]
        self._set_source_model(df)

    def clear(self):
        self.model().setSourceModel(None)
        self._df = None

    def _set_source_model(self, df: pd.DataFrame):
        model = PandasModel(df)
        self.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.setSortingEnabled(False)
        self.model().setSourceModel(model)
        self.setSortingEnabled(self._sorting)

    def set_sorting(self, state: bool):
        self._sorting = state
        self.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.setSortingEnabled(self._sorting)

    def resize_columns_width(self):
        self.resizeColumnsToContents()
