from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QKeyEvent, QIcon
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.modules.intellimaze.animalgate.data.animalgate_data import AnimalGateData
from tse_analytics.modules.intellimaze.animalgate.views.animalgate_dialog_ui import Ui_AnimalGateDialog
from tse_analytics.modules.intellimaze.animalgate.views.animalgate_table_view import AnimalGateTableView
from tse_analytics.modules.intellimaze.data.im_device_item import IMDeviceItem
from tse_analytics.modules.intellimaze.views.im_device_selector import IMDeviceSelector


class AnimalGateDialog(QDialog):
    def __init__(self, animalgate_data: AnimalGateData, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_AnimalGateDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("AnimalGateDialog/Geometry"))

        self.animalgate_data = animalgate_data

        self.sessions_table_view = AnimalGateTableView(self)
        self.sessions_table_view.set_data(self.animalgate_data.sessions_df)
        self.ui.tabWidget.addTab(self.sessions_table_view, "Sessions")

        self.antenna_table_view = AnimalGateTableView(self)
        self.antenna_table_view.set_data(self.animalgate_data.antenna_df)
        self.ui.tabWidget.addTab(self.antenna_table_view, "Antenna")

        self.log_table_view = AnimalGateTableView(self)
        self.log_table_view.set_data(self.animalgate_data.log_df)
        self.ui.tabWidget.addTab(self.log_table_view, "Log")

        self.input_table_view = AnimalGateTableView(self)
        self.input_table_view.set_data(self.animalgate_data.input_df)
        self.ui.tabWidget.addTab(self.input_table_view, "Input")

        self.output_table_view = AnimalGateTableView(self)
        self.output_table_view.set_data(self.animalgate_data.output_df)
        self.ui.tabWidget.addTab(self.output_table_view, "Output")

        self.ui.toolButtonPreprocess.clicked.connect(self._preprocess)
        self.ui.toolButtonExport.clicked.connect(self._export_data)

        device_ids = self.animalgate_data.log_df["DeviceId"].unique().tolist()
        self.device_selector = IMDeviceSelector(self._filter_devices)
        self.device_selector.set_data(device_ids)
        self.ui.toolBox.addItem(self.device_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Devices")

        self.selected_devices: list[IMDeviceItem] = []

    def _filter_devices(self, selected_devices: list[IMDeviceItem]):
        self.selected_devices = selected_devices

        sessions_df = self.animalgate_data.sessions_df
        antenna_df = self.animalgate_data.antenna_df
        log_df = self.animalgate_data.log_df
        if len(self.selected_devices) > 0:
            sessions_df = sessions_df[sessions_df["DeviceId"].isin(self.selected_devices)]
            antenna_df = antenna_df[antenna_df["DeviceId"].isin(self.selected_devices)]
            log_df = log_df[log_df["DeviceId"].isin(self.selected_devices)]

        self.sessions_table_view.set_data(sessions_df)
        self.sessions_table_view.set_data(antenna_df)
        self.sessions_table_view.set_data(log_df)

    def _preprocess(self) -> None:
        pass

    def _export_data(self):
        pass

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("AnimalGateDialog/Geometry", self.saveGeometry())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
