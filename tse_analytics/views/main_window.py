import os
from functools import partial
from pathlib import Path

import psutil
import PySide6QtAds
from pyqttoast import Toast
from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QLabel, QMainWindow, QMenu, QMessageBox, QToolButton

from tse_analytics.core import manager
from tse_analytics.core.helper import CSV_IMPORT_ENABLED, show_help
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.modules.phenomaster.io.tse_dataset_loader import load_tse_dataset
from tse_analytics.views.about_dialog import AboutDialog
from tse_analytics.views.analysis.ancova.ancova_widget import AncovaWidget
from tse_analytics.views.analysis.correlation.correlation_widget import CorrelationWidget
from tse_analytics.views.analysis.distribution.distribution_widget import DistributionWidget
from tse_analytics.views.analysis.histogram.histogram_widget import HistogramWidget
from tse_analytics.views.analysis.matrixplot.matrixplot_widget import MatrixPlotWidget
from tse_analytics.views.analysis.mixed_anova.mixed_anova_widget import MixedAnovaWidget
from tse_analytics.views.analysis.n_way_anova.n_way_anova_widget import NWayAnovaWidget
from tse_analytics.views.analysis.normality.normality_widget import NormalityWidget
from tse_analytics.views.analysis.one_way_anova.one_way_anova_widget import OneWayAnovaWidget
from tse_analytics.views.analysis.pca.pca_widget import PcaWidget
from tse_analytics.views.analysis.regression.regression_widget import RegressionWidget
from tse_analytics.views.analysis.rm_anova.rm_anova_widget import RMAnovaWidget
from tse_analytics.views.analysis.timeseries_autocorrelation.timeseries_autocorrelation_widget import (
    TimeseriesAutocorrelationWidget,
)
from tse_analytics.views.analysis.timeseries_decomposition.timeseries_decomposition_widget import (
    TimeseriesDecompositionWidget,
)
from tse_analytics.views.analysis.tsne.tsne_widget import TsneWidget
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

        self.add_widget_button = QToolButton()
        self.add_widget_button.setText("Add Widget")
        self.add_widget_button.setIcon(QIcon(":/icons/icons8-database-import-16.png"))
        self.add_widget_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.add_widget_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.add_widget_button.setEnabled(False)

        menu = QMenu("AddWidgetMenu", self.add_widget_button)
        data_menu = menu.addMenu("Data")
        data_menu.addAction(QIcon(":/icons/table.png"), "Table").triggered.connect(self._add_data_table_widget)
        data_menu.addAction(QIcon(":/icons/plot.png"), "Plot").triggered.connect(self._add_data_plot_widget)

        exploration_menu = menu.addMenu("Exploration")
        exploration_menu.addAction(QIcon(":/icons/exploration.png"), "Histogram").triggered.connect(
            self._add_histogram_widget
        )
        exploration_menu.addAction(QIcon(":/icons/exploration.png"), "Distribution").triggered.connect(
            self._add_distribution_widget
        )
        exploration_menu.addAction(QIcon(":/icons/exploration.png"), "Normality").triggered.connect(
            self._add_normality_widget
        )

        bivariate_menu = menu.addMenu("Bivariate")
        bivariate_menu.addAction(QIcon(":/icons/bivariate.png"), "Correlation").triggered.connect(
            self._add_correlation_widget
        )
        bivariate_menu.addAction(QIcon(":/icons/bivariate.png"), "Regression").triggered.connect(
            self._add_regression_widget
        )

        anova_menu = menu.addMenu("ANOVA")
        anova_menu.addAction(QIcon(":/icons/anova.png"), "One-way ANOVA").triggered.connect(
            self._add_one_way_anova_widget
        )
        anova_menu.addAction(QIcon(":/icons/anova.png"), "N-way ANOVA").triggered.connect(self._add_n_way_anova_widget)
        anova_menu.addAction(QIcon(":/icons/anova.png"), "Repeated Measures ANOVA").triggered.connect(
            self._add_rm_anova_widget
        )
        anova_menu.addAction(QIcon(":/icons/anova.png"), "Mixed-design ANOVA").triggered.connect(
            self._add_mixed_anova_widget
        )
        anova_menu.addAction(QIcon(":/icons/anova.png"), "ANCOVA").triggered.connect(self._add_ancova_widget)

        dimensionality_menu = menu.addMenu("Dimensionality")
        dimensionality_menu.addAction(QIcon(":/icons/dimensionality.png"), "Matrix Plot").triggered.connect(
            self._add_matrixplot_widget
        )
        dimensionality_menu.addAction(QIcon(":/icons/dimensionality.png"), "PCA").triggered.connect(
            self._add_pca_widget
        )
        dimensionality_menu.addAction(QIcon(":/icons/dimensionality.png"), "tSNE").triggered.connect(
            self._add_tsne_widget
        )

        utils_menu = menu.addMenu("Time Series")
        utils_menu.addAction(QIcon(":/icons/timeseries.png"), "Decomposition").triggered.connect(
            self._add_timeseries_decomposition_widget
        )
        utils_menu.addAction(QIcon(":/icons/timeseries.png"), "Autocorrelation").triggered.connect(
            self._add_timeseries_autocorrelation_widget
        )

        utils_menu = menu.addMenu("Utils")
        utils_menu.addAction(QIcon(":/icons/report.png"), "Report").triggered.connect(self._add_report_widget)
        self.add_widget_button.setMenu(menu)

        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.add_widget_button)

        # Initialize dock manager. Because the parent parameter is a QMainWindow
        # the dock manager registers itself as the central widget.
        LayoutManager(self, self.menuView)

        LayoutManager.set_central_widget()

        datasets_dock_widget = LayoutManager.register_dock_widget(
            DatasetsWidget(self), "Datasets", QIcon(":/icons/datasets.png")
        )
        datasets_dock_area = LayoutManager.add_dock_widget(PySide6QtAds.LeftDockWidgetArea, datasets_dock_widget)

        info_dock_widget = LayoutManager.register_dock_widget(InfoWidget(), "Info", QIcon(":/icons/info.png"))
        info_dock_area = LayoutManager.add_dock_widget_to_area(
            PySide6QtAds.BottomDockWidgetArea, info_dock_widget, datasets_dock_area
        )

        help_dock_widget = LayoutManager.register_dock_widget(HelpWidget(), "Help", QIcon(":/icons/help.png"))
        LayoutManager.add_dock_widget_tab_to_area(help_dock_widget, info_dock_area)

        log_dock_widget = LayoutManager.register_dock_widget(LogWidget(), "Log", QIcon(":/icons/log.png"))
        LayoutManager.add_dock_widget_tab_to_area(log_dock_widget, info_dock_area)
        info_dock_area.setCurrentIndex(0)

        animals_dock_widget = LayoutManager.register_dock_widget(
            AnimalsWidget(), "Animals", QIcon(":/icons/icons8-rat-silhouette-16.png")
        )
        animals_dock_area = LayoutManager.add_dock_widget(PySide6QtAds.RightDockWidgetArea, animals_dock_widget)

        factors_dock_widget = LayoutManager.register_dock_widget(
            FactorsWidget(), "Factors", QIcon(":/icons/factors.png")
        )
        selector_dock_area = LayoutManager.add_dock_widget_to_area(
            PySide6QtAds.BottomDockWidgetArea, factors_dock_widget, animals_dock_area
        )

        variables_dock_widget = LayoutManager.register_dock_widget(
            VariablesWidget(), "Variables", QIcon(":/icons/variables.png")
        )
        LayoutManager.add_dock_widget_tab_to_area(variables_dock_widget, selector_dock_area)
        selector_dock_area.setCurrentIndex(0)

        binning_dock_widget = LayoutManager.register_dock_widget(
            BinningSettingsWidget(), "Binning", QIcon(":/icons/binning.png")
        )
        LayoutManager.add_dock_widget_to_area(
            PySide6QtAds.BottomDockWidgetArea, binning_dock_widget, selector_dock_area
        )

        self.actionImportDataset.triggered.connect(self.import_dataset_dialog)
        self.actionOpenWorkspace.triggered.connect(self.load_workspace_dialog)
        self.actionSaveWorkspace.triggered.connect(self.save_workspace_dialog)
        self.actionExportCsv.triggered.connect(self.export_csv_dialog)
        self.actionExportExcel.triggered.connect(self.export_excel_dialog)
        self.actionSaveLayout.triggered.connect(self._save_layout)
        self.actionRestoreLayout.triggered.connect(self._restore_layout)
        self.actionResetLayout.triggered.connect(self._reset_layout)
        self.actionExit.triggered.connect(lambda: QApplication.exit())
        self.actionHelp.triggered.connect(lambda: show_help(self, "Introduction.md"))
        self.actionAbout.triggered.connect(self._show_about_dialog)

        # Store default dock layout
        LayoutManager.add_perspective("Default")

        self.load_settings()

        Toast.setPositionRelativeToWidget(self)
        Toast.setMovePositionWithWidget(True)
        self.toast = None

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
            LayoutManager.clear_dock_manager()
            manager.load_workspace(filename)
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
            LayoutManager.restore_state(state)

    def save_settings(self):
        settings = QSettings()
        settings.setValue("MainWindow/Geometry", self.saveGeometry())
        settings.setValue("MainWindow/State", self.saveState())
        settings.setValue("MainWindow/DockingState", LayoutManager.save_state())

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
            manager.save_workspace(filename)

    def export_excel_dialog(self) -> None:
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if filename:
            dataset.export_to_excel(filename)

    def export_csv_dialog(self) -> None:
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if filename:
            dataset.export_to_csv(filename)

    def update_memory_usage(self):
        # return the memory usage in MB
        mem = self.process.memory_info()[0] / float(2**20)
        self.memory_usage_label.setText(f"Memory usage: {mem:.2f} Mb")

    def _reset_layout(self):
        LayoutManager.open_perspective("Default")

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
                        manager.import_csv_dataset(path)
                elif path.suffix.lower() == ".tse":
                    dialog = ImportTseDialog(path, self)
                    # TODO: check other cases!!
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        import_settings = dialog.get_import_settings()

                        self.toast = make_toast(self, "Importing Dataset", "Please wait...")
                        self.toast.show()

                        worker = Worker(load_tse_dataset, path, import_settings)
                        worker.signals.result.connect(self._import_result)
                        worker.signals.finished.connect(self._import_finished)
                        TaskManager.start_task(worker)
                    dialog.deleteLater()

    def _import_result(self, dataset: Dataset) -> None:
        if dataset is not None:
            manager.get_workspace_model().add_dataset(dataset)

    def _import_finished(self) -> None:
        self.toast.hide()

    def _save_layout(self) -> None:
        LayoutManager.add_perspective("Temporary")

    def _restore_layout(self) -> None:
        LayoutManager.open_perspective("Temporary")

    def _add_data_table_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = DataTableWidget(dataset)
        LayoutManager.add_widget_to_central_area(dataset, widget, f"Table - {dataset.name}", QIcon(":/icons/table.png"))

    def _add_data_plot_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = DataPlotWidget(dataset)
        LayoutManager.add_widget_to_central_area(dataset, widget, f"Plot - {dataset.name}", QIcon(":/icons/plot.png"))

    def _add_histogram_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = HistogramWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/exploration.png")
        )

    def _add_distribution_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = DistributionWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/exploration.png")
        )

    def _add_normality_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = NormalityWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/exploration.png")
        )

    def _add_correlation_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = CorrelationWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/bivariate.png")
        )

    def _add_regression_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = RegressionWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/bivariate.png")
        )

    def _add_one_way_anova_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = OneWayAnovaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_n_way_anova_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = NWayAnovaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_rm_anova_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = RMAnovaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_mixed_anova_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = MixedAnovaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_ancova_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = AncovaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/anova.png")
        )

    def _add_matrixplot_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = MatrixPlotWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/dimensionality.png")
        )

    def _add_pca_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = PcaWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/dimensionality.png")
        )

    def _add_tsne_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = TsneWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/dimensionality.png")
        )

    def _add_timeseries_decomposition_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = TimeseriesDecompositionWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/timeseries.png")
        )

    def _add_timeseries_autocorrelation_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = TimeseriesAutocorrelationWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"{widget.title} - {dataset.name}", QIcon(":/icons/timeseries.png")
        )

    def _add_report_widget(self):
        dataset = manager.get_selected_dataset()
        if dataset is None:
            return
        widget = ReportsWidget(dataset)
        LayoutManager.add_widget_to_central_area(
            dataset, widget, f"Report - {dataset.name}", QIcon(":/icons/report.png")
        )

    def set_enabled_add_widget_button(self, enabled: bool):
        self.add_widget_button.setEnabled(enabled)

    def closeEvent(self, event: QCloseEvent) -> None:
        if QMessageBox.question(self, "TSE Analytics", "Do you want to quit?") == QMessageBox.StandardButton.Yes:
            LayoutManager.clear_dock_manager()
            self.save_settings()
            LayoutManager.delete_dock_manager()
            super().closeEvent(event)
        else:
            event.ignore()
