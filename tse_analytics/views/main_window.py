import os
from functools import partial

import psutil
import PySide6QtAds
from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QLabel, QMainWindow

from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.ancova_widget import AncovaWidget
from tse_analytics.views.analysis.anova_widget import AnovaWidget
from tse_analytics.views.analysis.correlation_widget import CorrelationWidget
from tse_analytics.views.analysis.distribution_widget import DistributionWidget
from tse_analytics.views.analysis.glm_widget import GlmWidget
from tse_analytics.views.analysis.histogram_widget import HistogramWidget
from tse_analytics.views.analysis.normality_widget import NormalityWidget
from tse_analytics.views.analysis.pca_widget import PcaWidget
from tse_analytics.views.analysis.scatter_matrix_widget import ScatterMatrixWidget
from tse_analytics.views.data.plot_view_widget import PlotViewWidget
from tse_analytics.views.data.table_view_widget import TableViewWidget
from tse_analytics.views.datasets.datasets_tree_view import DatasetsTreeView
from tse_analytics.views.help.help_widget import HelpWidget
from tse_analytics.views.info.info_widget import InfoWidget
from tse_analytics.views.main_window_ui import Ui_MainWindow
from tse_analytics.views.selection.animals.animals_view_widget import AnimalsViewWidget
from tse_analytics.views.selection.factors.factors_view_widget import FactorsViewWidget
from tse_analytics.views.selection.variables.variables_view_widget import (
    VariablesViewWidget,
)
from tse_analytics.views.settings.binning_widget import BinningWidget
from tse_analytics.workspace.layout import LAYOUT_VERSION

PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.ActiveTabHasCloseButton, False)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.DockAreaHasCloseButton, False)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.DockAreaDynamicTabsMenuButtonVisibility, True)
PySide6QtAds.CDockManager.setConfigFlag(PySide6QtAds.CDockManager.FloatingContainerHasWidgetIcon, True)


MAX_RECENT_FILES = 10


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

        self.menuOpenRecent.aboutToShow.connect(self.populate_open_recent)

        # Create the dock manager. Because the parent parameter is a QMainWindow
        # the dock manager registers itself as the central widget.
        self.dock_manager = PySide6QtAds.CDockManager(self)
        self.default_docking_state = None

        data_table_dock_widget = PySide6QtAds.CDockWidget("Data")
        data_table_dock_widget.setWidget(TableViewWidget())
        data_table_dock_widget.setIcon(QIcon(":/icons/icons8-data-sheet-16.png"))
        main_area = self.dock_manager.addDockWidget(PySide6QtAds.AllDockAreas, data_table_dock_widget)

        plot_table_dock_widget = PySide6QtAds.CDockWidget("Plot")
        plot_table_dock_widget.setWidget(PlotViewWidget())
        plot_table_dock_widget.setIcon(QIcon(":/icons/icons8-line-chart-16.png"))
        self.dock_manager.addDockWidgetTabToArea(plot_table_dock_widget, main_area)

        histogram_dock_widget = PySide6QtAds.CDockWidget("Histogram")
        histogram_dock_widget.setIcon(QIcon(":/icons/icons8-scales-16.png"))
        histogram_dock_widget.setWidget(HistogramWidget())
        self.dock_manager.addDockWidgetTabToArea(histogram_dock_widget, main_area)

        distribution_dock_widget = PySide6QtAds.CDockWidget("Distribution")
        distribution_dock_widget.setIcon(QIcon(":/icons/icons8-bar-chart-16.png"))
        distribution_dock_widget.setWidget(DistributionWidget())
        self.dock_manager.addDockWidgetTabToArea(distribution_dock_widget, main_area)

        normality_dock_widget = PySide6QtAds.CDockWidget("Normality")
        normality_dock_widget.setIcon(QIcon(":/icons/icons8-approval-16.png"))
        normality_dock_widget.setWidget(NormalityWidget())
        self.dock_manager.addDockWidgetTabToArea(normality_dock_widget, main_area)

        correlation_dock_widget = PySide6QtAds.CDockWidget("Correlation")
        correlation_dock_widget.setIcon(QIcon(":/icons/icons8-scales-16.png"))
        correlation_dock_widget.setWidget(CorrelationWidget())
        self.dock_manager.addDockWidgetTabToArea(correlation_dock_widget, main_area)

        anova_dock_widget = PySide6QtAds.CDockWidget("ANOVA")
        anova_dock_widget.setIcon(QIcon(":/icons/icons8-scales-16.png"))
        anova_dock_widget.setWidget(AnovaWidget())
        self.dock_manager.addDockWidgetTabToArea(anova_dock_widget, main_area)

        ancova_dock_widget = PySide6QtAds.CDockWidget("ANCOVA")
        ancova_dock_widget.setIcon(QIcon(":/icons/icons8-scales-16.png"))
        ancova_dock_widget.setWidget(AncovaWidget())
        self.dock_manager.addDockWidgetTabToArea(ancova_dock_widget, main_area)

        glm_dock_widget = PySide6QtAds.CDockWidget("GLM")
        glm_dock_widget.setIcon(QIcon(":/icons/icons8-scales-16.png"))
        glm_dock_widget.setWidget(GlmWidget())
        self.dock_manager.addDockWidgetTabToArea(glm_dock_widget, main_area)

        matrix_dock_widget = PySide6QtAds.CDockWidget("Matrix")
        matrix_dock_widget.setIcon(QIcon(":/icons/icons8-scales-16.png"))
        matrix_dock_widget.setWidget(ScatterMatrixWidget())
        self.dock_manager.addDockWidgetTabToArea(matrix_dock_widget, main_area)

        pca_dock_widget = PySide6QtAds.CDockWidget("PCA")
        pca_dock_widget.setIcon(QIcon(":/icons/icons8-scales-16.png"))
        pca_dock_widget.setWidget(PcaWidget())
        self.dock_manager.addDockWidgetTabToArea(pca_dock_widget, main_area)

        datasets_dock_widget = PySide6QtAds.CDockWidget("Datasets")
        datasets_dock_widget.setWidget(DatasetsTreeView())
        datasets_dock_widget.setIcon(QIcon(":/icons/icons8-data-sheet-16.png"))
        datasets_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        datasets_dock_area = self.dock_manager.addDockWidget(PySide6QtAds.LeftDockWidgetArea, datasets_dock_widget)

        info_dock_widget = PySide6QtAds.CDockWidget("Info")
        info_dock_widget.setWidget(InfoWidget())
        info_dock_widget.setIcon(QIcon(":/icons/icons8-data-sheet-16.png"))
        info_dock_area = self.dock_manager.addDockWidget(
            PySide6QtAds.BottomDockWidgetArea, info_dock_widget, datasets_dock_area
        )

        help_dock_widget = PySide6QtAds.CDockWidget("Help")
        help_dock_widget.setWidget(HelpWidget())
        help_dock_widget.setIcon(QIcon(":/icons/icons8-data-sheet-16.png"))
        self.dock_manager.addDockWidgetTabToArea(help_dock_widget, info_dock_area)

        animals_dock_widget = PySide6QtAds.CDockWidget("Animals")
        animals_dock_widget.setWidget(AnimalsViewWidget())
        animals_dock_widget.setIcon(QIcon(":/icons/icons8-rat-silhouette-16.png"))
        animals_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        selector_dock_area = self.dock_manager.addDockWidget(PySide6QtAds.RightDockWidgetArea, animals_dock_widget)

        factors_dock_widget = PySide6QtAds.CDockWidget("Factors")
        factors_dock_widget.setWidget(FactorsViewWidget())
        factors_dock_widget.setIcon(QIcon(":/icons/icons8-group-objects-16.png"))
        self.dock_manager.addDockWidgetTabToArea(factors_dock_widget, selector_dock_area)

        variables_dock_widget = PySide6QtAds.CDockWidget("Variables")
        variables_dock_widget.setWidget(VariablesViewWidget())
        variables_dock_widget.setIcon(QIcon(":/icons/icons8-group-objects-16.png"))
        self.dock_manager.addDockWidgetTabToArea(variables_dock_widget, selector_dock_area)

        binning_dock_widget = PySide6QtAds.CDockWidget("Binning")
        binning_dock_widget.setWidget(BinningWidget())
        binning_dock_widget.setIcon(QIcon(":/icons/icons8-time-span-16.png"))
        binning_dock_widget.setMinimumSizeHintMode(PySide6QtAds.CDockWidget.MinimumSizeHintFromContent)
        self.dock_manager.addDockWidget(PySide6QtAds.BottomDockWidgetArea, binning_dock_widget, selector_dock_area)

        self.actionImportDataset.triggered.connect(self.import_dataset_dialog)
        self.actionOpenWorkspace.triggered.connect(self.load_workspace_dialog)
        self.actionSaveWorkspace.triggered.connect(self.save_workspace_dialog)
        self.actionExportExcel.triggered.connect(self.export_excel_dialog)
        self.actionExportCsv.triggered.connect(self.export_csv_dialog)
        self.actionResetLayout.triggered.connect(self.__reset_layout)
        self.actionExit.triggered.connect(lambda: QApplication.exit())

        # self.dock_manager.setDockWidgetFocused(animals_dock_widget)

        self.default_docking_state = self.dock_manager.saveState(LAYOUT_VERSION)

        self.load_settings()

    def populate_open_recent(self):
        # Step 1. Remove the old options from the menu
        self.menuOpenRecent.clear()
        # Step 2. Dynamically create the actions
        actions = []
        settings = QSettings()
        filenames = list(settings.value('recentFilesList', []))
        for filename in filenames:
            action = QAction(filename, self)
            action.triggered.connect(partial(self.load_workspace, filename))
            actions.append(action)
        # Step 3. Add the actions to the menu
        self.menuOpenRecent.addActions(actions)

    def load_workspace(self, filename: str):
        settings = QSettings()
        filenames = list(settings.value('recentFilesList', []))
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
            self.load_workspace(file_path)

    def save_workspace_dialog(self):
        file_ext = "*.workspace"
        dialog = QFileDialog(self)
        dialog.setDefaultSuffix(".workspace")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setWindowTitle("Save Workspace")
        dialog.setNameFilter("Workspace Files ({})".format(file_ext))
        if dialog.exec() == QDialog.Accepted:
            Manager.save_workspace(dialog.selectedFiles()[0])

    def export_excel_dialog(self):
        file_ext = "*.xlsx"
        dialog = QFileDialog(self)
        dialog.setDefaultSuffix(".xlsx")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setWindowTitle("Export to Excel")
        dialog.setNameFilter("Excel Files ({})".format(file_ext))
        if dialog.exec() == QDialog.Accepted:
            Manager.data.export_to_excel(dialog.selectedFiles()[0])

    def export_csv_dialog(self):
        file_ext = "*.csv"
        dialog = QFileDialog(self)
        dialog.setDefaultSuffix(".csv")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setWindowTitle("Export to CSV")
        dialog.setNameFilter("CSV Files ({})".format(file_ext))
        if dialog.exec() == QDialog.Accepted:
            Manager.data.export_to_csv(dialog.selectedFiles()[0])

    def update_memory_usage(self):
        # return the memory usage in MB
        mem = self.process.memory_info()[0] / float(2**20)
        self.memory_usage_label.setText(f"Memory usage: {mem:.2f} Mb")

    def import_dataset(self, path: str):
        Manager.import_dataset(path)

    def __reset_layout(self):
        self.dock_manager.restoreState(self.default_docking_state, LAYOUT_VERSION)

    def import_dataset_dialog(self):
        options = QFileDialog.Options()
        file_ext = "*.csv"
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import dataset",
            "",
            "Dataset Files ({})".format(file_ext),
            options=options,
        )
        if path:
            self.import_dataset(path)

    @property
    def okToQuit(self):
        return True

    def closeEvent(self, event):
        if self.okToQuit:
            self.save_settings()
