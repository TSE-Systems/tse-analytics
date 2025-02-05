import pandas as pd
from PySide6.QtWidgets import QWidget

from tse_analytics.core.models.pandas_simple_model import PandasSimpleModel
from tse_analytics.modules.phenomaster.trafficage.data.trafficage_data import TraffiCageData
from tse_analytics.modules.phenomaster.trafficage.views.trafficage_raw_data_widget_ui import Ui_TraffiCageRawDataWidget


class TraffiCageRawDataWidget(QWidget):
    def __init__(self, data: TraffiCageData, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_TraffiCageRawDataWidget()
        self.ui.setupUi(self)

        self.data = data

        self.ui.listWidgetTables.addItems([
            "RFID",
        ])
        self.ui.listWidgetTables.itemSelectionChanged.connect(self._table_selection_changed)

        self.ui.listWidgetBoxes.addItems(list(map(str, self.data.device_ids)))
        self.ui.listWidgetBoxes.itemSelectionChanged.connect(self._boxes_selection_changed)

        self.df: pd.DataFrame | None = None
        self.selected_boxes: list[int] = []

        self.ui.listWidgetTables.setCurrentRow(0)

    def _table_selection_changed(self):
        selected_table = self.ui.listWidgetTables.selectedItems()[0].text()
        match selected_table:
            case "RFID":
                self.df = self.data.raw_df
        self._set_data()
        self.ui.tableView.resizeColumnsToContents()

    def _boxes_selection_changed(self):
        self.selected_boxes = [int(item.text()) for item in self.ui.listWidgetBoxes.selectedItems()]
        self._set_data()

    def _set_data(self) -> None:
        df = self.df
        if len(self.selected_boxes) > 0:
            df = df[df["BoxNo"].isin(self.selected_boxes)]
        model = PandasSimpleModel(df)
        self.ui.tableView.setModel(model)
