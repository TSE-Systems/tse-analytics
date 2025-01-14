from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QKeyEvent, QIcon
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.modules.intellimaze.running_wheel.data.running_wheel_data import RunningWheelData
from tse_analytics.modules.intellimaze.running_wheel.views.running_wheel_dialog_ui import Ui_RunningWheelDialog
from tse_analytics.modules.intellimaze.views.im_device_selector import IMDeviceSelector
from tse_analytics.modules.intellimaze.views.im_table_view import IMTableView


class RunningWheelDialog(QDialog):
    def __init__(self, data: RunningWheelData, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_RunningWheelDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("RunningWheelDialog/Geometry"))

        self.data = data

        self.registration_table_view = IMTableView(self)
        self.registration_table_view.set_data(self.data.registration_df)
        self.ui.tabWidget.addTab(self.registration_table_view, "Registration")

        self.model_table_view = IMTableView(self)
        self.model_table_view.set_data(self.data.model_df)
        self.ui.tabWidget.addTab(self.model_table_view, "Model")

        self.preprocessed_view = None

        self.ui.toolButtonPreprocess.clicked.connect(self._preprocess)
        self.ui.toolButtonExport.clicked.connect(self._export_data)

        self.device_selector = IMDeviceSelector(self.data.device_ids, self._filter_devices, self.ui.toolBox)
        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(self.device_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Devices")

        self.selected_devices: list[str] = []

    def _filter_devices(self, selected_devices: list[str]):
        self.selected_devices = selected_devices

        registration_df = self.data.registration_df
        model_df = self.data.model_df
        if len(self.selected_devices) > 0:
            registration_df = registration_df[registration_df["DeviceId"].isin(self.selected_devices)]
            model_df = model_df[model_df["DeviceId"].isin(self.selected_devices)]

        self.registration_table_view.set_data(registration_df)
        self.model_table_view.set_data(model_df)

    def _preprocess(self) -> None:
        if self.preprocessed_view is None:
            self.preprocessed_view = IMTableView(self)
            self.ui.tabWidget.addTab(self.preprocessed_view, "Preprocessed")
        df, variables = self.data.get_preprocessed_data()
        self.preprocessed_view.set_data(df)

    def _export_data(self):
        pass

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("RunningWheelDialog/Geometry", self.saveGeometry())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
