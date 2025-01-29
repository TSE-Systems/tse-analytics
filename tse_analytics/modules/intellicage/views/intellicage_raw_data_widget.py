import pandas as pd
from PySide6.QtWidgets import QWidget

from tse_analytics.core.models.pandas_simple_model import PandasSimpleModel
from tse_analytics.modules.intellicage.data.intellicage_raw_data import IntelliCageRawData
from tse_analytics.modules.intellicage.views.intellicage_raw_data_widget_ui import Ui_IntelliCageRawDataWidget


class IntelliCageRawDataWidget(QWidget):
    def __init__(self, data: IntelliCageRawData, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_IntelliCageRawDataWidget()
        self.ui.setupUi(self)

        self.data = data

        self.ui.listWidgetTables.addItems([
            "Visits",
            "Nosepokes",
            "Environment",
            "HardwareEvents",
            "Log",
        ])
        self.ui.listWidgetTables.itemSelectionChanged.connect(self._table_selection_changed)

        self.ui.listWidgetCages.addItems(list(map(str, self.data.device_ids)))
        self.ui.listWidgetCages.itemSelectionChanged.connect(self._cages_selection_changed)

        self.df: pd.DataFrame | None = None
        self.selected_cages: list[int] = []

        self.ui.listWidgetTables.setCurrentRow(0)

    def _table_selection_changed(self):
        selected_table = self.ui.listWidgetTables.selectedItems()[0].text()
        match selected_table:
            case "Visits":
                self.df = self.data.visits_df
            case "Nosepokes":
                self.df = self.data.nosepokes_df
            case "Environment":
                self.df = self.data.environment_df
            case "HardwareEvents":
                self.df = self.data.hardware_events_df
            case _:
                self.df = self.data.log_df
        self._set_data()
        self.ui.tableView.resizeColumnsToContents()

    def _cages_selection_changed(self):
        self.selected_cages = [int(item.text()) for item in self.ui.listWidgetCages.selectedItems()]
        self._set_data()

    def _set_data(self) -> None:
        df = self.df
        if len(self.selected_cages) > 0 and "Cage" in df.columns:
            df = df[df["Cage"].isin(self.selected_cages)]
        model = PandasSimpleModel(df)
        self.ui.tableView.setModel(model)
