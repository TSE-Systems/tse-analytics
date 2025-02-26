import os
import zipfile
from functools import partial
from pathlib import Path

import PySide6QtAds
import psutil
from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QDesktopServices
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QLabel, QMainWindow, QMessageBox
from pyqttoast import Toast, ToastPreset

from tse_analytics.core import manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.helper import CSV_IMPORT_ENABLED, IS_RELEASE
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.intellicage.io.dataset_loader import import_intellicage_dataset
from tse_analytics.modules.intellimaze.io.dataset_loader import import_im_dataset
from tse_analytics.modules.phenomaster.io.tse_dataset_loader import load_tse_dataset
from tse_analytics.views.about_dialog import AboutDialog
from tse_analytics.views.datasets.datasets_widget import DatasetsWidget
from tse_analytics.views.import_csv_dialog import ImportCsvDialog
from tse_analytics.views.import_tse_dialog import ImportTseDialog
from tse_analytics.views.info.info_widget import InfoWidget
from tse_analytics.views.log_widget import LogWidget
from tse_analytics.views.main_window_ui import Ui_MainWindow
from tse_analytics.views.misc.add_widget_button import AddWidgetButton
from tse_analytics.views.selection.animals.animals_widget import AnimalsWidget
from tse_analytics.views.selection.factors.factors_widget import FactorsWidget
from tse_analytics.views.selection.variables.variables_widget import VariablesWidget
from tse_analytics.views.settings.binning_settings_widget import BinningSettingsWidget

MAX_RECENT_FILES = 10


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.settings = QSettings()

        self.process = psutil.Process(os.getpid())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_memory_usage)
        self.ui_timer.start(1000)

        self.memory_usage_label = QLabel()
        self.statusBar.addPermanentWidget(self.memory_usage_label)

        self.menuOpenRecent.aboutToShow.connect(self.populate_open_recent)

        self.add_widget_button = AddWidgetButton(self)

        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.add_widget_button)

        # Initialize dock manager. Because the parent parameter is a QMainWindow
        # the dock manager registers itself as the central widget.
        LayoutManager(self, self.menuView)

        self.menuStyle.addAction("Default").triggered.connect(lambda: self.set_style("default"))
        self.menuStyle.addAction("TSE Light").triggered.connect(lambda: self.set_style("tse-light"))
        # self.menuStyle.addAction("TSE Dark").triggered.connect(lambda: self.set_style("tse-dark"))

        LayoutManager.set_central_widget()

        datasets_dock_widget = LayoutManager.register_dock_widget(
            DatasetsWidget(self, self.add_widget_button), "Datasets", QIcon(":/icons/datasets.png")
        )
        datasets_dock_area = LayoutManager.add_dock_widget(PySide6QtAds.LeftDockWidgetArea, datasets_dock_widget)

        info_dock_widget = LayoutManager.register_dock_widget(InfoWidget(), "Info", QIcon(":/icons/info.png"))
        info_dock_area = LayoutManager.add_dock_widget_to_area(
            PySide6QtAds.BottomDockWidgetArea, info_dock_widget, datasets_dock_area
        )

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
        self.actionHelp.triggered.connect(
            lambda: QDesktopServices.openUrl("https://tse-systems.github.io/tse-analytics-docs")
        )
        self.actionAbout.triggered.connect(self._show_about_dialog)

        # Store default dock layout
        LayoutManager.add_perspective("Default")

        self.load_settings()

        Toast.setPositionRelativeToWidget(self)
        Toast.setMovePositionWithWidget(True)
        self.toast = None

    def set_style(self, name: str) -> None:
        style_file = f"_internal/styles/qss/{name}.css" if IS_RELEASE else f"styles/qss/{name}.css"
        with open(style_file) as file:
            # Set global stylesheet
            QApplication.instance().setStyleSheet(file.read())
        self.settings.setValue("appStyle", name)

    def populate_open_recent(self):
        # Step 1. Remove the old options from the menu
        self.menuOpenRecent.clear()
        # Step 2. Dynamically create the actions
        actions = []
        filenames = list(self.settings.value("recentFilesList", []))
        for filename in filenames:
            action = QAction(filename, self)
            action.triggered.connect(partial(self.load_workspace, filename))
            actions.append(action)
        # Step 3. Add the actions to the menu
        self.menuOpenRecent.addActions(actions)

    def load_workspace(self, filename: str):
        filenames = list(self.settings.value("recentFilesList", []))
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
            self.settings.setValue("recentFilesList", filenames)

    def load_settings(self):
        self.restoreGeometry(self.settings.value("MainWindow/Geometry"))
        self.restoreState(self.settings.value("MainWindow/State"))

        state = self.settings.value("MainWindow/DockingState")
        if state is not None:
            LayoutManager.restore_state(state)

    def save_settings(self):
        self.settings.setValue("MainWindow/Geometry", self.saveGeometry())
        self.settings.setValue("MainWindow/State", self.saveState())
        self.settings.setValue("MainWindow/DockingState", LayoutManager.save_state())

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

    def import_dataset_dialog(self) -> None:
        filter = (
            "Data Files (*.tse *.csv *.zip);;TSE Dataset Files (*.tse);;CSV Files (*.csv);;IntelliMaze Dataset Files (*.zip)"
            if CSV_IMPORT_ENABLED
            else "Data Files (*.tse *.zip);;TSE Dataset Files (*.tse);;IntelliMaze Dataset Files (*.zip)"
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
                match path.suffix.lower():
                    case ".csv":
                        dialog = ImportCsvDialog(str(path), self)
                        # TODO: check other cases!!
                        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                        if dialog.exec() == QDialog.DialogCode.Accepted:
                            manager.import_csv_dataset(path)
                    case ".tse":
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
                    case ".zip":
                        if not zipfile.is_zipfile(path):
                            make_toast(
                                self,
                                "TSE Analytics",
                                "Wrong ZIP file format.",
                                duration=3000,
                                preset=ToastPreset.WARNING,
                            ).show()
                            return

                        with zipfile.ZipFile(path, mode="r") as zip:
                            archived_files = zip.namelist()

                        if any(".IntelliMaze" in sub for sub in archived_files):
                            self.toast = make_toast(self, "Importing IntelliMaze Dataset", "Please wait...")
                            self.toast.show()

                            worker = Worker(import_im_dataset, path)
                            worker.signals.result.connect(self._import_result)
                            worker.signals.finished.connect(self._import_finished)
                            TaskManager.start_task(worker)
                        elif any(".experiment" in sub for sub in archived_files):
                            self.toast = make_toast(self, "Importing IntelliCage Dataset", "Please wait...")
                            self.toast.show()

                            worker = Worker(import_intellicage_dataset, path)
                            worker.signals.result.connect(self._import_result)
                            worker.signals.finished.connect(self._import_finished)
                            TaskManager.start_task(worker)
                        else:
                            make_toast(
                                self,
                                "TSE Analytics",
                                "Zip archive is not an IntelliMaze/IntelliCage dataset.",
                                duration=3000,
                                preset=ToastPreset.WARNING,
                            ).show()

    def _import_result(self, dataset: Dataset) -> None:
        if dataset is not None:
            manager.get_workspace_model().add_dataset(dataset)

    def _import_finished(self) -> None:
        self.toast.hide()

    def _save_layout(self) -> None:
        LayoutManager.add_perspective("Temporary")

    def _restore_layout(self) -> None:
        LayoutManager.open_perspective("Temporary")

    def closeEvent(self, event: QCloseEvent) -> None:
        if (
            QMessageBox.question(
                self,
                "TSE Analytics",
                "Do you want to quit?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            LayoutManager.clear_dock_manager()
            self.save_settings()
            LayoutManager.delete_dock_manager()
            super().closeEvent(event)
        else:
            event.ignore()
