from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.modules.intellimaze.submodules.consumption_scale.data.consumption_scale_data import (
    ConsumptionScaleData,
)
from tse_analytics.modules.intellimaze.submodules.consumption_scale.views.consumption_scale_dialog_ui import (
    Ui_ConsumptionScaleDialog,
)
from tse_analytics.views.misc.device_selector import DeviceSelector
from tse_analytics.views.misc.pandas_table_view import PandasTableView


class ConsumptionScaleDialog(QDialog):
    def __init__(self, data: ConsumptionScaleData, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ConsumptionScaleDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("ConsumptionScaleDialog/Geometry"))

        self.data = data

        self.consumption_table_view = PandasTableView(self)
        self.consumption_table_view.set_data(self.data.consumption_df)
        self.ui.tabWidget.addTab(self.consumption_table_view, "Consumption")

        self.model_table_view = PandasTableView(self)
        self.model_table_view.set_data(self.data.model_df)
        self.ui.tabWidget.addTab(self.model_table_view, "Model")

        self.preprocessed_view = None

        self.ui.toolButtonPreprocess.clicked.connect(self._preprocess)
        self.ui.toolButtonExport.clicked.connect(self._export_data)

        self.device_selector = DeviceSelector(self.data.device_ids, self._filter_devices, self.ui.toolBox)
        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(self.device_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Devices")

        self.selected_devices: list[str] = []

    def _filter_devices(self, selected_devices: list[str]):
        self.selected_devices = selected_devices

        consumption_df = self.data.consumption_df
        model_df = self.data.model_df
        if len(self.selected_devices) > 0:
            consumption_df = consumption_df[consumption_df["DeviceId"].isin(self.selected_devices)]
            model_df = model_df[model_df["DeviceId"].isin(self.selected_devices)]

        self.consumption_table_view.set_data(consumption_df)
        self.model_table_view.set_data(model_df)

    def _preprocess(self) -> None:
        if self.preprocessed_view is None:
            self.preprocessed_view = PandasTableView(self)
            self.ui.tabWidget.addTab(self.preprocessed_view, "Preprocessed")
        df, variables = self.data.get_preprocessed_data()
        self.preprocessed_view.set_data(df)

    def _export_data(self):
        pass

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("ConsumptionScaleDialog/Geometry", self.saveGeometry())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
