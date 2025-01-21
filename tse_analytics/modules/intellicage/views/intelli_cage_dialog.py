from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.modules.intellicage.data.intelli_cage_data import IntelliCageData
from tse_analytics.modules.intellicage.views.intelli_cage_dialog_ui import Ui_IntelliCageDialog
from tse_analytics.views.misc.device_selector import DeviceSelector
from tse_analytics.views.misc.pandas_table_view import PandasTableView


class IntelliCageDialog(QDialog):
    def __init__(self, data: IntelliCageData, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_IntelliCageDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("IntelliCageDialog/Geometry"))

        self.data = data

        self.visits_table_view = PandasTableView(self)
        self.visits_table_view.set_data(self.data.visits_df)
        self.ui.tabWidget.addTab(self.visits_table_view, "Visits")

        self.nosepokes_table_view = PandasTableView(self)
        self.nosepokes_table_view.set_data(self.data.nosepokes_df)
        self.ui.tabWidget.addTab(self.nosepokes_table_view, "Nosepokes")

        self.environment_table_view = PandasTableView(self)
        self.environment_table_view.set_data(self.data.environment_df)
        self.ui.tabWidget.addTab(self.environment_table_view, "Environment")

        self.hardware_events_table_view = PandasTableView(self)
        self.hardware_events_table_view.set_data(self.data.hardware_events_df)
        self.ui.tabWidget.addTab(self.hardware_events_table_view, "HardwareEvents")

        self.log_table_view = PandasTableView(self)
        self.log_table_view.set_data(self.data.log_df)
        self.ui.tabWidget.addTab(self.log_table_view, "Log")

        self.preprocessed_view = None

        self.ui.toolButtonPreprocess.clicked.connect(self._preprocess)
        self.ui.toolButtonExport.clicked.connect(self._export_data)

        self.device_selector = DeviceSelector(self.data.device_ids, self._filter_devices, self.ui.toolBox)
        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(self.device_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Cages")

        self.selected_devices: list[int] = []

    def _filter_devices(self, selected_devices: list[str]):
        self.selected_devices = list(map(int, selected_devices))

        visits_df = self.data.visits_df
        # nosepokes_df = self.data.nosepokes_df
        environment_df = self.data.environment_df
        hardware_events_df = self.data.hardware_events_df
        log_df = self.data.log_df
        if len(self.selected_devices) > 0:
            visits_df = visits_df[visits_df["Cage"].isin(self.selected_devices)]
            # nosepokes_df = nosepokes_df[nosepokes_df["Cage"].isin(self.selected_devices)]
            environment_df = environment_df[environment_df["Cage"].isin(self.selected_devices)]
            hardware_events_df = hardware_events_df[hardware_events_df["Cage"].isin(self.selected_devices)]
            log_df = log_df[log_df["Cage"].isin(self.selected_devices)]

        self.visits_table_view.set_data(visits_df)
        # self.nosepokes_table_view.set_data(nosepokes_df)
        self.environment_table_view.set_data(environment_df)
        self.hardware_events_table_view.set_data(hardware_events_df)
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
        settings.setValue("IntelliCageDialog/Geometry", self.saveGeometry())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
