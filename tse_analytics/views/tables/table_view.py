from typing import Optional

from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QWidget, QTableView, QHeaderView

from tse_datatools.analysis.processor import apply_time_binning
from tse_datatools.data.animal import Animal

from tse_analytics.messaging.messages import BinningAppliedMessage
from tse_analytics.models.pandas_model import PandasModel
from tse_datatools.data.dataset import Dataset


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
        self._data: Optional[Dataset] = None
        self._animal_ids: Optional[list[int]] = None

    def set_data(self, data: Dataset):
        self._data = data
        model = PandasModel(data.df)
        self._set_source_model(model)

    def set_animal_data(self, animals: list[Animal]):
        self._animal_ids = [animal.id for animal in animals]
        if self._data:
            df = self._data.df
            df = df[df['Animal'].isin(self._animal_ids)]
            model = PandasModel(df)
            self._set_source_model(model)

    def clear(self):
        self.model().setSourceModel(None)
        self._data = None
        self._animal_ids = None

    def apply_binning(self, message: BinningAppliedMessage):
        df = self._data.df

        result = apply_time_binning(df, message.delta, message.unit, message.mode)

        model = PandasModel(result)
        self._set_source_model(model)

    def _set_source_model(self, model: PandasModel):
        self.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.setSortingEnabled(False)
        self.model().setSourceModel(model)
        self.setSortingEnabled(self._sorting)

    def set_sorting(self, state: bool):
        self._sorting = state
        self.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.setSortingEnabled(self._sorting)
