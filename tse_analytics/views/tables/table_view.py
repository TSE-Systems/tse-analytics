from typing import Optional

from PySide6.QtCore import Qt, QSortFilterProxyModel, QItemSelection
from PySide6.QtWidgets import QWidget, QTableView, QHeaderView
from tse_datatools.data.animal import Animal
from tse_datatools.data.dataset_component import DatasetComponent

from tse_analytics.messaging.messages import BinningAppliedMessage
from tse_analytics.models.pandas_model import PandasModel


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
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setSortingEnabled(True)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

        self._data: Optional[DatasetComponent] = None
        self._animal_ids: Optional[list[int]] = None

    def set_data(self, data: DatasetComponent):
        self._data = data
        model = PandasModel(data.df)
        self.model().setSourceModel(model)

    def set_animal_data(self, animals: list[Animal]):
        self._animal_ids = [animal.id for animal in animals]
        if self._data:
            df = self._data.df
            df = df[df['AnimalNo'].isin(self._animal_ids)]
            model = PandasModel(df)
            self.model().setSourceModel(model)

    def clear(self):
        self.model().setSourceModel(None)
        self._data = None
        self._animal_ids = None

    def apply_binning(self, message: BinningAppliedMessage):
        df = self._data.df
        df = df[df['AnimalNo'].isin(self._animal_ids)]
        df = df.set_index('DateTime', drop=False)

        unit = "H"
        if message.unit == "Day":
            unit = "D"
        elif message.unit == "Hour":
            unit = "H"
        elif message.unit == "Minute":
            unit = "min"
        rule = f'{message.delta}{unit}'

        if message.mode == "Mean":
            result = df.resample(rule, on='DateTime').mean()
        elif message.mode == "Median":
            result = df.resample(rule, on='DateTime').median()
        else:
            result = df.resample(rule, on='DateTime').sum()

        model = PandasModel(result)
        self.model().setSourceModel(model)


    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        # proxy_model: QSortFilterProxyModel = self.model()
        # model = proxy_model.sourceModel()
        # selected_animals: Set[str] = set()
        # for index in self.selectedIndexes():
        #     if index.column() != 0:
        #         continue
        #     if index.isValid():
        #         source_index = proxy_model.mapToSource(index)
        #         row = source_index.row()
        #         channel = model.channels[row]
        #         selected_animals.add(channel[1])
        # if len(selected_animals) < 7:
        #     Manager.messenger.broadcast(SelectedAnimalsChangedMessage(self, selected_animals))
        pass
