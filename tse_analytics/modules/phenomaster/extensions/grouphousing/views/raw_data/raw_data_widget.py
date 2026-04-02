import pandas as pd
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.extensions.grouphousing.data.grouphousing_data import GroupHousingData
from tse_analytics.modules.phenomaster.extensions.grouphousing.views.raw_data.raw_data_widget_ui import (
    Ui_RawDataWidget,
)
from tse_analytics.toolbox.data_table.data_table_widget import DataTableWidget


class RawDataWidget(QWidget):
    def __init__(
        self,
        data: GroupHousingData,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.data = data

        self.ui = Ui_RawDataWidget()
        self.ui.setupUi(self)

        self.tableView = DataTableWidget(self.data.raw_datatable, "Raw Data")
        self.ui.tableLayout.addWidget(self.tableView)

        self.ui.listWidgetAnimals.addItems(list(map(str, self.data.animal_ids)))
        self.ui.listWidgetAnimals.itemSelectionChanged.connect(self._animals_selection_changed)

    def _table_selection_changed(self):
        self._set_data()

    def _animals_selection_changed(self):
        self._set_data()

    def _get_filtered_df(self) -> pd.DataFrame:
        df = self.data.raw_datatable.df
        selected_animals = [item.text() for item in self.ui.listWidgetAnimals.selectedItems()]
        if len(selected_animals) > 0:
            df = df[df["Animal"].isin(selected_animals)]
        return df

    def _set_data(self):
        df = self._get_filtered_df()

        new_datatable = self.data.raw_datatable.clone()
        new_datatable.df = df

        self.tableView.set_datatable(new_datatable)
