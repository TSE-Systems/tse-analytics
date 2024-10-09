import os
from functools import partial
from pathlib import Path

import psutil
import PySide6QtAds
from pyqttoast import Toast
from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QLabel, QMainWindow, QMessageBox, QWidget

from tse_analytics.core.helper import CSV_IMPORT_ENABLED, LAYOUT_VERSION, show_help
from tse_analytics.core.manager import Manager
from tse_analytics.views.about_dialog import AboutDialog
from tse_analytics.views.analysis.anova_widget import AnovaWidget
from tse_analytics.views.analysis.bivariate_widget import BivariateWidget
from tse_analytics.views.analysis.dimensionality_widget import DimensionalityWidget
from tse_analytics.views.analysis.exploration_widget import ExplorationWidget
from tse_analytics.views.analysis.timeseries.timeseries_widget import TimeseriesWidget
from tse_analytics.views.data.data_plot_widget import DataPlotWidget
from tse_analytics.views.data.data_table_widget import DataTableWidget
from tse_analytics.views.datasets.datasets_widget import DatasetsWidget
from tse_analytics.views.help.help_widget import HelpWidget
from tse_analytics.views.import_csv_dialog import ImportCsvDialog
from tse_analytics.views.import_tse_dialog import ImportTseDialog
from tse_analytics.views.info.info_widget import InfoWidget
from tse_analytics.views.log_widget import LogWidget
from tse_analytics.views.main_window_ui import Ui_MainWindow
from tse_analytics.views.reports.reports_widget import ReportsWidget
from tse_analytics.views.selection.animals.animals_widget import AnimalsWidget
from tse_analytics.views.selection.factors.factors_widget import FactorsWidget
from tse_analytics.views.selection.variables.variables_widget import VariablesWidget
from tse_analytics.views.settings.binning_settings_widget import BinningSettingsWidget

PySide6QtAds.CDockManager.setConfigFlags(PySide6QtAds.CDockManager.DefaultOpaqueConfig)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.ActiveTabHasCloseButton, False)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.DockAreaHasCloseButton, False)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.DockAreaHasUndockButton, False)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.DockAreaDynamicTabsMenuButtonVisibility, True)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.FloatingContainerHasWidgetIcon, True)

# PySide6QtAds.CDockManager.setAutoHideConfigFlags(PySide6QtAds.CDockManager.DefaultAutoHideConfig)
# PySide6QtAds.CDockManager.setAutoHideConfigFlag(PySide6QtAds.CDockManager.AutoHideFeatureEnabled, True)
# PySide6QtAds.CDockManager.setAutoHideConfigFlag(PySide6QtAds.CDockManager.DockAreaHasAutoHideButton, False)
# PySide6QtAds.CDockManager.setAutoHideConfigFlag(PySide6QtAds.CDockManager.AutoHideHasCloseButton, False)

MAX_RECENT_FILES = 10


class MainWindow(QMainWindow, Ui_MainWindow):
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

        # Create the dock manager. Because the parent parameter is a QMainWindow
        # the dock manager registers itself as the central widget.
        self.dock_manager = PySide6QtAds.CDockManager(self)
        self.dock_manager.setStyleSheet("")

        self.default_docking_state = None

        data_table_dock_widget = self._register_dock_widget(DataTableWidget(), "Table", QIcon(":/icons/table.png"))
        main_area = self.dock_manager.addDockWidget(PySide6QtAds.AllDockAreas, data_table_dock_widget)

        data_plot_dock_widget = self._register_dock_widget(DataPlotWidget(), "Plot", QIcon(":/icons/plot.png"))
        self.dock_manager.addDockWidgetTabToArea(data_plot_dock_widget, main_area)

        exploration_widget = self._register_dock_widget(
            ExplorationWidget(), "Exploration", QIcon(":/icons/exploration.png")
        )
        self.dock_manager.addDockWidgetTabToArea(exploration_widget, main_area)

        bivariate_dock_widget = self._register_dock_widget(
            BivariateWidget(), "Bivariate", QIcon(":/icons/bivariate.png")
        )
        self.dock_manager.addDockWidgetTabToArea(bivariate_dock_widget, main_area)

        anova_dock_widget = self._register_dock_widget(AnovaWidget(), "AN(C)OVA", QIcon(":/icons/anova.png"))
        self.dock_manager.addDockWidgetTabToArea(anova_dock_widget, main_area)

        dimensionality_dock_widget = self._register_dock_widget(
            DimensionalityWidget(), "Dimensionality", QIcon(":/icons/dimensionality.png")
        )
        self.dock_manager.addDockWidgetTabToArea(dimensionality_dock_widget, main_area)

        timeseries_dock_widget = self._register_dock_widget(
            TimeseriesWidget(), "Timeseries", QIcon(":/icons/timeseries.png")
        )
        self.dock_manager.addDockWidgetTabToArea(timeseries_dock_widget, main_area)

        report_dock_widget = self._register_dock_widget(ReportsWidget(), "Report", QIcon(":/icons/report.png"))
        self.dock_manager.addDockWidgetTabToArea(report_dock_widget, main_area)

        datasets_dock_widget = self._register_dock_widget(DatasetsWidget(), "Datasets", QIcon(":/icons/datasets.png"))
        datasets_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        datasets_dock_area = self.dock_manager.addDockWidget(PySide6QtAds.LeftDockWidgetArea, datasets_dock_widget)

        info_dock_widget = self._register_dock_widget(InfoWidget(), "Info", QIcon(":/icons/info.png"))
        info_dock_area = self.dock_manager.addDockWidget(
            PySide6QtAds.BottomDockWidgetArea, info_dock_widget, datasets_dock_area
        )

        help_dock_widget = self._register_dock_widget(HelpWidget(), "Help", QIcon(":/icons/help.png"))
        self.dock_manager.addDockWidgetTabToArea(help_dock_widget, info_dock_area)

        log_dock_widget = self._register_dock_widget(LogWidget(), "Log", QIcon(":/icons/log.png"))
        self.dock_manager.addDockWidgetTabToArea(log_dock_widget, info_dock_area)

        animals_dock_widget = self._register_dock_widget(
            AnimalsWidget(), "Animals", QIcon(":/icons/icons8-rat-silhouette-16.png")
        )
        animals_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        animals_dock_area = self.dock_manager.addDockWidget(PySide6QtAds.RightDockWidgetArea, animals_dock_widget)

        factors_dock_widget = self._register_dock_widget(FactorsWidget(), "Factors", QIcon(":/icons/factors.png"))
        factors_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        selector_dock_area = self.dock_manager.addDockWidget(
            PySide6QtAds.BottomDockWidgetArea, factors_dock_widget, animals_dock_area
        )

        variables_dock_widget = self._register_dock_widget(
            VariablesWidget(), "Variables", QIcon(":/icons/variables.png")
        )
        variables_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        self.dock_manager.addDockWidgetTabToArea(variables_dock_widget, selector_dock_area)

        binning_dock_widget = self._register_dock_widget(
            BinningSettingsWidget(), "Binning", QIcon(":/icons/binning.png")
        )
        binning_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        self.dock_manager.addDockWidget(PySide6QtAds.BottomDockWidgetArea, binning_dock_widget, selector_dock_area)

        self.actionImportDataset.triggered.connect(self.import_dataset_dialog)
        self.actionOpenWorkspace.triggered.connect(self.load_workspace_dialog)
        self.actionSaveWorkspace.triggered.connect(self.save_workspace_dialog)
        self.actionExportCsv.triggered.connect(self.export_csv_dialog)
        self.actionExportExcel.triggered.connect(self.export_excel_dialog)
        self.actionResetLayout.triggered.connect(self._reset_layout)
        self.actionExit.triggered.connect(lambda: QApplication.exit())
        self.actionHelp.triggered.connect(lambda: show_help(self, "main.md"))
        self.actionAbout.triggered.connect(self._show_about_dialog)

        self.default_docking_state = self.dock_manager.saveState(LAYOUT_VERSION)

        self.load_settings()

        Toast.setPositionRelativeToWidget(self)
        Toast.setMovePositionWithWidget(True)

    def _register_dock_widget(self, widget: QWidget, title: str, icon: QIcon) -> PySide6QtAds.CDockWidget:
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

    def update_memory_usage(self):
        # return the memory usage in MB
        mem = self.process.memory_info()[0] / float(2**20)
        self.memory_usage_label.setText(f"Memory usage: {mem:.2f} Mb")

    def _reset_layout(self):
        self.dock_manager.restoreState(self.default_docking_state, LAYOUT_VERSION)

    def _show_about_dialog(self):
        dlg = AboutDialog(self)
        dlg.show()

    def import_dataset_dialog(self):
        filter = (
            "Data Files (*.tse *.csv);;TSE Dataset Files (*.tse);;CSV Files (*.csv)"
            if CSV_IMPORT_ENABLED
            else "TSE Dataset Files (*.tse)"
        )
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import dataset",
            "",
            filter,
        )
        if filename:
            path = Path(filename)
            if path.is_file():
                if path.suffix.lower() == ".csv":
                    dialog = ImportCsvDialog(str(path), self)
                    # TODO: check other cases!!
                    dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        Manager.import_csv_dataset(path)
                elif path.suffix.lower() == ".tse":
                    dialog = ImportTseDialog(path, self)
                    # TODO: check other cases!!
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        import_settings = dialog.get_import_settings()
                        Manager.import_tse_dataset(path, import_settings)
                    dialog.deleteLater()

    def closeEvent(self, event: QCloseEvent) -> None:
        if QMessageBox.question(self, "TSE Analytics", "Do you want to quit?") == QMessageBox.StandardButton.Yes:
            self.save_settings()
            event.accept()
        else:
            event.ignore()
