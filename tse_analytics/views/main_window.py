import os
from functools import partial

import psutil
import PySide6QtAds
from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QFileDialog, QLabel, QMainWindow, QMessageBox, QWidget

from tse_analytics.core.data.shared import GroupingMode
from tse_analytics.core.helper import LAYOUT_VERSION, show_help
from tse_analytics.core.licensing import LicenseManager
from tse_analytics.core.manager import Manager
from tse_analytics.views.about_dialog import AboutDialog
from tse_analytics.views.analysis.anova_widget import AnovaWidget
from tse_analytics.views.analysis.correlation_widget import CorrelationWidget
from tse_analytics.views.analysis.distribution_widget import DistributionWidget
from tse_analytics.views.analysis.glm_widget import GlmWidget
from tse_analytics.views.analysis.histogram_widget import HistogramWidget
from tse_analytics.views.analysis.matrix_widget import MatrixWidget
from tse_analytics.views.analysis.normality_widget import NormalityWidget
from tse_analytics.views.analysis.pca_widget import PcaWidget
from tse_analytics.views.analysis.timeseries.timeseries_widget import TimeseriesWidget
from tse_analytics.views.data.data_plot_widget import DataPlotWidget
from tse_analytics.views.data.data_table_widget import DataTableWidget
from tse_analytics.views.datasets.datasets_tree_view import DatasetsTreeView
from tse_analytics.views.exclude_time_dialog import ExcludeTimeDialog
from tse_analytics.views.help.help_widget import HelpWidget
from tse_analytics.views.info.info_widget import InfoWidget
from tse_analytics.views.log_widget import LogWidget
from tse_analytics.views.main_window_ui import Ui_MainWindow
from tse_analytics.views.selection.animals.animals_widget import AnimalsWidget
from tse_analytics.views.selection.factors.factors_widget import FactorsWidget
from tse_analytics.views.selection.variables.variables_widget import VariablesWidget
from tse_analytics.views.settings.binning_settings_widget import BinningSettingsWidget
from tse_analytics.views.settings.outliers_settings_widget import OutliersSettingsWidget
from tse_analytics.views.tools.compare_runs_widget import CompareRunsWidget

PySide6QtAds.CDockManager.setConfigFlags(PySide6QtAds.CDockManager.DefaultOpaqueConfig)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.ActiveTabHasCloseButton, False)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.DockAreaHasCloseButton, False)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.DockAreaHasUndockButton, False)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.DockAreaDynamicTabsMenuButtonVisibility, True)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.FloatingContainerHasWidgetIcon, True)


MAX_RECENT_FILES = 10


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.process = psutil.Process(os.getpid())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_memory_usage)
        self.ui_timer.start(1000)

        self.memory_usage_label = QLabel()
        self.statusBar.addPermanentWidget(self.memory_usage_label)

        self.menuOpenRecent.aboutToShow.connect(self.populate_open_recent)
        self.menuTools.aboutToShow.connect(self.__tools_availability)

        self.toolBar.addWidget(QLabel("Grouping Mode: "))
        grouping_mode_combo_box = QComboBox()
        grouping_mode_combo_box.addItems([e.value for e in GroupingMode])
        grouping_mode_combo_box.currentTextChanged.connect(self.__grouping_mode_changed)
        self.toolBar.addWidget(grouping_mode_combo_box)

        # Create the dock manager. Because the parent parameter is a QMainWindow
        # the dock manager registers itself as the central widget.
        self.dock_manager = PySide6QtAds.CDockManager(self)
        self.dock_manager.setStyleSheet("")

        self.default_docking_state = None

        data_table_dock_widget = self.__register_dock_widget(
            DataTableWidget(), "Data", QIcon(":/icons/icons8-data-sheet-16.png")
        )
        main_area = self.dock_manager.addDockWidget(PySide6QtAds.AllDockAreas, data_table_dock_widget)

        plot_table_dock_widget = self.__register_dock_widget(
            DataPlotWidget(), "Plot", QIcon(":/icons/icons8-line-chart-16.png")
        )
        self.dock_manager.addDockWidgetTabToArea(plot_table_dock_widget, main_area)

        histogram_dock_widget = self.__register_dock_widget(
            HistogramWidget(), "Histogram", QIcon(":/icons/icons8-histogram-16.png")
        )
        self.dock_manager.addDockWidgetTabToArea(histogram_dock_widget, main_area)

        distribution_dock_widget = self.__register_dock_widget(
            DistributionWidget(), "Distribution", QIcon(":/icons/icons8-bar-chart-16.png")
        )
        self.dock_manager.addDockWidgetTabToArea(distribution_dock_widget, main_area)

        normality_dock_widget = self.__register_dock_widget(
            NormalityWidget(), "Normality", QIcon(":/icons/icons8-approval-16.png")
        )
        self.dock_manager.addDockWidgetTabToArea(normality_dock_widget, main_area)

        correlation_dock_widget = self.__register_dock_widget(
            CorrelationWidget(), "Correlation", QIcon(":/icons/icons8-scales-16.png")
        )
        self.dock_manager.addDockWidgetTabToArea(correlation_dock_widget, main_area)

        anova_dock_widget = self.__register_dock_widget(
            AnovaWidget(), "AN(C)OVA", QIcon(":/icons/icons8-scales-16.png")
        )
        self.dock_manager.addDockWidgetTabToArea(anova_dock_widget, main_area)

        glm_dock_widget = self.__register_dock_widget(GlmWidget(), "GLM", QIcon(":/icons/icons8-scales-16.png"))
        self.dock_manager.addDockWidgetTabToArea(glm_dock_widget, main_area)

        matrix_dock_widget = self.__register_dock_widget(
            MatrixWidget(), "Matrix", QIcon(":/icons/icons8-heat-map-16.png")
        )
        self.dock_manager.addDockWidgetTabToArea(matrix_dock_widget, main_area)

        pca_dock_widget = self.__register_dock_widget(PcaWidget(), "PCA", QIcon(":/icons/icons8-scales-16.png"))
        self.dock_manager.addDockWidgetTabToArea(pca_dock_widget, main_area)

        timeseries_dock_widget = self.__register_dock_widget(
            TimeseriesWidget(), "Timeseries", QIcon(":/icons/time.svg")
        )
        self.dock_manager.addDockWidgetTabToArea(timeseries_dock_widget, main_area)

        datasets_dock_widget = self.__register_dock_widget(
            DatasetsTreeView(), "Datasets", QIcon(":/icons/icons8-database-16.png")
        )
        datasets_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        datasets_dock_area = self.dock_manager.addDockWidget(PySide6QtAds.LeftDockWidgetArea, datasets_dock_widget)

        info_dock_widget = self.__register_dock_widget(InfoWidget(), "Info", QIcon(":/icons/icons8-info-16.png"))
        info_dock_area = self.dock_manager.addDockWidget(
            PySide6QtAds.BottomDockWidgetArea, info_dock_widget, datasets_dock_area
        )

        help_dock_widget = self.__register_dock_widget(HelpWidget(), "Help", QIcon(":/icons/icons8-help-16.png"))
        self.dock_manager.addDockWidgetTabToArea(help_dock_widget, info_dock_area)

        log_dock_widget = self.__register_dock_widget(LogWidget(), "Log", QIcon(":/icons/log-16.png"))
        self.dock_manager.addDockWidgetTabToArea(log_dock_widget, info_dock_area)

        animals_dock_widget = self.__register_dock_widget(
            AnimalsWidget(), "Animals", QIcon(":/icons/icons8-rat-silhouette-16.png")
        )
        animals_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        selector_dock_area = self.dock_manager.addDockWidget(PySide6QtAds.RightDockWidgetArea, animals_dock_widget)

        factors_dock_widget = self.__register_dock_widget(
            FactorsWidget(), "Factors", QIcon(":/icons/icons8-dog-tag-16.png")
        )
        self.dock_manager.addDockWidgetTabToArea(factors_dock_widget, selector_dock_area)

        variables_dock_widget = self.__register_dock_widget(
            VariablesWidget(), "Variables", QIcon(":/icons/icons8-variable-16.png")
        )
        self.dock_manager.addDockWidgetTabToArea(variables_dock_widget, selector_dock_area)

        binning_dock_widget = self.__register_dock_widget(
            BinningSettingsWidget(), "Binning", QIcon(":/icons/icons8-time-span-16.png")
        )
        binning_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        settings_dock_area = self.dock_manager.addDockWidget(
            PySide6QtAds.BottomDockWidgetArea, binning_dock_widget, selector_dock_area
        )

        outliers_dock_widget = self.__register_dock_widget(
            OutliersSettingsWidget(), "Outliers", QIcon(":/icons/icons8-outliers-16.png")
        )
        self.dock_manager.addDockWidgetTabToArea(outliers_dock_widget, settings_dock_area)

        self.actionImportDataset.triggered.connect(self.import_dataset_dialog)
        self.actionOpenWorkspace.triggered.connect(self.load_workspace_dialog)
        self.actionSaveWorkspace.triggered.connect(self.save_workspace_dialog)
        self.actionExportCsv.triggered.connect(self.export_csv_dialog)
        self.actionExportExcel.triggered.connect(self.export_excel_dialog)
        self.actionExportSQLite.triggered.connect(self.export_sqlite_dialog)
        self.actionResetLayout.triggered.connect(self.__reset_layout)
        self.actionExit.triggered.connect(lambda: QApplication.exit())
        self.actionCompareRuns.triggered.connect(self.__compare_runs)
        self.actionExcludeAnimals.triggered.connect(self.__exclude_animals)
        self.actionExcludeTime.triggered.connect(self.__exclude_time)
        self.actionHelp.triggered.connect(lambda: show_help(self, "main.md"))
        self.actionAbout.triggered.connect(self.__show_about_dialog)

        self.default_docking_state = self.dock_manager.saveState(LAYOUT_VERSION)

        self.compare_runs_widget: CompareRunsWidget | None = None

        self.load_settings()

        self.__check_license()

    def __check_license(self):
        if LicenseManager.is_license_missing():
            self.statusBar.showMessage("License is missing!")
        elif LicenseManager.is_license_expired():
            self.statusBar.showMessage("License has expired!")
        elif LicenseManager.is_hardware_id_invalid():
            self.statusBar.showMessage("License Hardware ID is invalid!")

        if (
            LicenseManager.is_license_missing()
            or LicenseManager.is_license_expired()
            or LicenseManager.is_hardware_id_invalid()
            or LicenseManager.is_feature_missing("PhenoMaster")
        ):
            self.actionImportDataset.setDisabled(True)
            self.actionExportCsv.setDisabled(True)
            self.actionExportExcel.setDisabled(True)

    def __register_dock_widget(self, widget: QWidget, title: str, icon: QIcon) -> PySide6QtAds.CDockWidget:
        dock_widget = PySide6QtAds.CDockWidget(title)
        dock_widget.setWidget(widget)
        dock_widget.setIcon(icon)
        self.menuView.insertAction(self.actionResetLayout, dock_widget.toggleViewAction())
        return dock_widget

    def populate_open_recent(self):
        # Step 1. Remove the old options from the menu
        self.menuOpenRecent.clear()
        # Step 2. Dynamically create the actions
        actions = []
        settings = QSettings()
        filenames = list(settings.value("recentFilesList", []))
        for filename in filenames:
            action = QAction(filename, self)
            action.triggered.connect(partial(self.load_workspace, filename))
            actions.append(action)
        # Step 3. Add the actions to the menu
        self.menuOpenRecent.addActions(actions)

    def load_workspace(self, filename: str):
        settings = QSettings()
        filenames = list(settings.value("recentFilesList", []))
        try:
            filenames.remove(filename)
        except ValueError:
            pass

        try:
            Manager.load_workspace(filename)
            filenames.insert(0, filename)
            del filenames[MAX_RECENT_FILES:]
        finally:
            settings.setValue("recentFilesList", filenames)

    def load_settings(self):
        settings = QSettings()
        self.restoreGeometry(settings.value("MainWindow/Geometry"))
        self.restoreState(settings.value("MainWindow/State"))

        state = settings.value("MainWindow/DockingState")
        if state is not None:
            self.dock_manager.restoreState(state, LAYOUT_VERSION)

    def save_settings(self):
        settings = QSettings()
        settings.setValue("MainWindow/Geometry", self.saveGeometry())
        settings.setValue("MainWindow/State", self.saveState())
        settings.setValue("MainWindow/DockingState", self.dock_manager.saveState(LAYOUT_VERSION))

    def load_workspace_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Workspace",
            "",
            "Workspace Files (*.workspace)",
        )
        if file_path:
            self.load_workspace(file_path)

    def save_workspace_dialog(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save TSE Analytics Workspace", "", "Workspace Files (*.workspace)"
        )
        if filename:
            Manager.save_workspace(filename)

    def export_excel_dialog(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if filename:
            Manager.data.export_to_excel(filename)

    def export_csv_dialog(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "Excel Files (*.csv)")
        if filename:
            Manager.data.export_to_csv(filename)

    def export_sqlite_dialog(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export to SQLite",
            Manager.data.selected_dataset.name if Manager.data.selected_dataset is not None else "",
            "SQLite Files (*.db)",
        )
        if filename:
            Manager.data.export_to_sqlite(filename)

    def update_memory_usage(self):
        # return the memory usage in MB
        mem = self.process.memory_info()[0] / float(2**20)
        self.memory_usage_label.setText(f"Memory usage: {mem:.2f} Mb")

    def __reset_layout(self):
        self.dock_manager.restoreState(self.default_docking_state, LAYOUT_VERSION)

    def __grouping_mode_changed(self, text: str):
        Manager.data.set_grouping_mode(GroupingMode(text))

    def __tools_availability(self):
        self.actionCompareRuns.setEnabled(
            Manager.data.selected_dataset is not None and Manager.data.selected_dataset.runs_count > 1
        )
        self.actionExcludeAnimals.setEnabled(Manager.data.selected_dataset is not None)
        self.actionExcludeTime.setEnabled(Manager.data.selected_dataset is not None)

    def __compare_runs(self):
        if self.compare_runs_widget is None:
            self.compare_runs_widget = CompareRunsWidget(self)
            self.compare_runs_widget.setWindowFlag(Qt.WindowType.Tool)
        self.compare_runs_widget.show()

    def __exclude_animals(self):
        if (
            QMessageBox.question(self, "Exclude Animals", "Do you really want to exclude selected animals?")
            == QMessageBox.StandardButton.Yes
        ):
            Manager.data.exclude_animals()

    def __exclude_time(self):
        min_datetime = Manager.data.selected_dataset.start_timestamp
        max_datetime = Manager.data.selected_dataset.end_timestamp
        dialog = ExcludeTimeDialog(min_datetime, max_datetime, self)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            start = dialog.dateTimeEditStart.dateTime().toPython()
            end = dialog.dateTimeEditEnd.dateTime().toPython()
            Manager.data.exclude_time(start, end)
        dialog.destroy()

    def __show_about_dialog(self):
        dlg = AboutDialog(self)
        dlg.show()
        self.__check_license()

    def import_dataset_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import dataset",
            "",
            "Dataset Files (*.csv)",
        )
        if path:
            Manager.import_dataset(path)

    @property
    def ok_to_quit(self):
        return True

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.ok_to_quit:
            self.save_settings()
