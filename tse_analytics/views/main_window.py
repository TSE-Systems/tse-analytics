import os
import psutil

from PySide6.QtCore import Qt, QTimer, QSettings, QByteArray
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QLabel,
    QApplication,
    QDialog, QComboBox)

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import ViewModeChangedMessage
from tse_analytics.core.view_mode import ViewMode
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_analytics.views.charts.aggregation_plot_view_widget import AggregationPlotViewWidget
from tse_analytics.views.charts.plot_view_widget import PlotViewWidget
from tse_analytics.views.groups.groups_view_widget import GroupsViewWidget
from tse_analytics.views.tables.table_view_widget import TableViewWidget
from tse_analytics.views.animals.animals_view_widget import AnimalsViewWidget
from tse_analytics.views.info.info_widget import InfoWidget
from tse_analytics.views.main_window_ui import Ui_MainWindow
from tse_analytics.views.settings.settings_widget import SettingsWidget
from tse_analytics.views.datasets.datasets_tree_view import DatasetsTreeView


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.process = psutil.Process(os.getpid())
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_memory_usage)
        self.ui_timer.start(1000)

        self.memory_usage_label = QLabel()
        self.statusBar.addPermanentWidget(self.memory_usage_label)

        self.workspace_tree_view = DatasetsTreeView()
        self.verticalLayoutOverview.addWidget(self.workspace_tree_view)

        self.info_widget = InfoWidget()
        self.verticalLayoutInfo.addWidget(self.info_widget)

        self.animals_view_widget = AnimalsViewWidget()
        self.tabWidgetSelection.addTab(self.animals_view_widget, QIcon(":/icons/icons8-rat-silhouette-16.png"), "Animals")

        self.groups_view_widget = GroupsViewWidget()
        self.tabWidgetSelection.addTab(self.groups_view_widget, QIcon(":/icons/icons8-group-objects-16.png"), "Groups")

        self.table_view_widget = TableViewWidget()
        self.tabWidget.addTab(self.table_view_widget, QIcon(":/icons/icons8-data-sheet-16.png"), "Table")

        # self.plot_view_widget = ChartViewWidget()
        # self.tabWidget.addTab(self.plot_view_widget, QIcon(":/icons/icons8-scatter-plot-16.png"), "Plot")

        self.plot_view_widget2 = PlotViewWidget()
        self.tabWidget.addTab(self.plot_view_widget2, QIcon(":/icons/icons8-line-chart-16.png"), "Timeline")

        self.aggregation_plot_view_widget = AggregationPlotViewWidget()
        self.tabWidget.addTab(self.aggregation_plot_view_widget, QIcon(":/icons/icons8-bar-chart-16.png"), "Aggregation")

        self.analysis_widget = AnalysisWidget()
        self.tabWidget.addTab(self.analysis_widget, QIcon(":/icons/icons8-statistics-16.png"), "Analysis")

        # self.tiles_view_widget = TilesViewWidget()
        # self.tabWidget.addTab(self.tiles_view_widget, QIcon(":/icons/icons8-medium-icons-16.png"), "Tiles")

        self.settings_widget = SettingsWidget()
        self.verticalLayoutSettings.addWidget(self.settings_widget)

        self.actionImportDataset.triggered.connect(self.import_dataset_dialog)
        self.actionOpenWorkspace.triggered.connect(self.load_workspace_dialog)
        self.actionSaveWorkspace.triggered.connect(self.save_workspace_dialog)
        self.actionExportExcel.triggered.connect(self.export_excel_dialog)
        self.actionExit.triggered.connect(lambda: QApplication.exit())

        self.toolBar.addWidget(QLabel("Mode: "))

        mode_combo_box = QComboBox()
        mode_combo_box.addItems([e.value for e in ViewMode])
        mode_combo_box.currentTextChanged.connect(self._mode_current_text_changed)
        self.toolBar.addWidget(mode_combo_box)

        self.load_settings()

    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value("MainWindow/Geometry", QByteArray()))
        self.restoreState(settings.value("MainWindow/State", QByteArray()))

    def save_settings(self):
        settings = QSettings()
        settings.setValue("MainWindow/Geometry", self.saveGeometry())
        settings.setValue("MainWindow/State", self.saveState())

    def load_workspace_dialog(self):
        options = QFileDialog.Options()
        file_ext = "*.workspace"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Workspace",
            "",
            "Workspace Files ({})".format(file_ext),
            options=options,
        )
        if file_path:
            Manager.data.load_workspace(file_path)

    def save_workspace_dialog(self):
        file_ext = "*.workspace"
        dialog = QFileDialog(self)
        dialog.setDefaultSuffix(".workspace")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setWindowTitle("Save Workspace")
        dialog.setNameFilter("Workspace Files ({})".format(file_ext))
        if dialog.exec() == QDialog.Accepted:
            Manager.data.save_workspace(dialog.selectedFiles()[0])

    def export_excel_dialog(self):
        file_ext = "*.xlsx"
        dialog = QFileDialog(self)
        dialog.setDefaultSuffix(".xlsx")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setWindowTitle("Export to Excel")
        dialog.setNameFilter("Excel Files ({})".format(file_ext))
        if dialog.exec() == QDialog.Accepted:
            Manager.data.export_to_excel(dialog.selectedFiles()[0])

    def update_memory_usage(self):
        # return the memory usage in MB
        mem = self.process.memory_info()[0] / float(2 ** 20)
        self.memory_usage_label.setText(f"Memory usage: {mem:.2f} Mb")

    def import_dataset(self, path: str):
        Manager.data.import_dataset(path)

    def import_dataset_dialog(self):
        options = QFileDialog.Options()
        path = QFileDialog.getExistingDirectory(
            self,
            "Select dataset folder",
            options=options
        )
        if path:
            self.import_dataset(path)

    @property
    def okToQuit(self):
        return True

    def closeEvent(self, event):
        if self.okToQuit:
            self.save_settings()

    def _mode_current_text_changed(self, text: str):
        Manager.messenger.broadcast(ViewModeChangedMessage(self, ViewMode(text)))
