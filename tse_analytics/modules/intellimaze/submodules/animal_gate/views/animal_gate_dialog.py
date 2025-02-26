from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.modules.intellimaze.submodules.animal_gate.data.animal_gate_data import AnimalGateData
from tse_analytics.modules.intellimaze.submodules.animal_gate.views.animal_gate_dialog_ui import Ui_AnimalGateDialog
from tse_analytics.views.misc.device_selector import DeviceSelector
from tse_analytics.views.misc.pandas_list_view import PandasListView
from tse_analytics.views.misc.pandas_table_view import PandasTableView


class AnimalGateDialog(QDialog):
    def __init__(self, data: AnimalGateData, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_AnimalGateDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("AnimalGateDialog/Geometry"))

        self.data = data

        self.sessions_table_view = PandasTableView(self)
        self.sessions_table_view.set_data(self.data.sessions_df)
        self.ui.tabWidget.addTab(self.sessions_table_view, "Sessions")

        self.antenna_table_view = PandasTableView(self)
        self.antenna_table_view.set_data(self.data.antenna_df)
        self.ui.tabWidget.addTab(self.antenna_table_view, "Antenna")

        self.log_table_view = PandasTableView(self)
        self.log_table_view.set_data(self.data.log_df)
        self.ui.tabWidget.addTab(self.log_table_view, "Log")

        self.input_list_view = PandasListView(self)
        self.input_list_view.set_data(self.data.input_df)
        self.ui.tabWidget.addTab(self.input_list_view, "Input")

        self.output_list_view = PandasListView(self)
        self.output_list_view.set_data(self.data.output_df)
        self.ui.tabWidget.addTab(self.output_list_view, "Output")

        self.preprocessed_view = None

        self.ui.toolButtonPreprocess.clicked.connect(self._preprocess)
        self.ui.toolButtonExport.clicked.connect(self._export_data)

        self.device_selector = DeviceSelector(self.data.device_ids, self._filter_devices, self.ui.toolBox)
        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(self.device_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Devices")

        self.selected_devices: list[str] = []

    def _filter_devices(self, selected_devices: list[str]):
        self.selected_devices = selected_devices

        sessions_df = self.data.sessions_df
        antenna_df = self.data.antenna_df
        log_df = self.data.log_df
        if len(self.selected_devices) > 0:
            sessions_df = sessions_df[sessions_df["DeviceId"].isin(self.selected_devices)]
            antenna_df = antenna_df[antenna_df["DeviceId"].isin(self.selected_devices)]
            log_df = log_df[log_df["DeviceId"].isin(self.selected_devices)]

        self.sessions_table_view.set_data(sessions_df)
        self.antenna_table_view.set_data(antenna_df)
        self.log_table_view.set_data(log_df)

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
        settings.setValue("AnimalGateDialog/Geometry", self.saveGeometry())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
