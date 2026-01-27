import os
import zipfile
from functools import partial
from pathlib import Path

import psutil
import PySide6QtAds
from pyqttoast import Toast, ToastPreset
from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QLabel, QMainWindow, QMessageBox

from tse_analytics.core import help_manager, manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.layouts.layout_manager import LayoutManager
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import CSV_IMPORT_ENABLED, IS_RELEASE
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.modules.intellicage.io.dataset_loader import import_intellicage_dataset
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset
from tse_analytics.modules.intellimaze.io.dataset_loader import import_intellimaze_dataset
from tse_analytics.modules.intellimaze.views.export_merged_csv.export_merged_csv_dialog import ExportMergedCsvDialog
from tse_analytics.modules.phenomaster.io.tse_dataset_loader import load_tse_dataset
from tse_analytics.modules.phenomaster.views.import_csv_dialog import ImportCsvDialog
from tse_analytics.modules.phenomaster.views.import_tse_dialog import ImportTseDialog
from tse_analytics.toolbox.toolbox_button import ToolboxButton
from tse_analytics.views.about.about_dialog import AboutDialog
from tse_analytics.views.animals.animals_widget import AnimalsWidget
from tse_analytics.views.datasets.datasets_widget import DatasetsWidget
from tse_analytics.views.factors.factors_widget import FactorsWidget
from tse_analytics.views.info.info_widget import InfoWidget
from tse_analytics.views.logs.log_widget import LogWidget
from tse_analytics.views.main_window_ui import Ui_MainWindow
from tse_analytics.views.pipeline.pipeline_editor_widget import PipelineEditorWidget
from tse_analytics.views.settings.binning_settings_widget import BinningSettingsWidget
from tse_analytics.views.settings.settings_dialog import SettingsDialog
from tse_analytics.views.variables.variables_widget import VariablesWidget

MAX_RECENT_FILES = 10


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.settings = QSettings()

        self.process = psutil.Process(os.getpid())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self._update_memory_usage)
        self.ui_timer.start(1000)

        self.memory_usage_label = QLabel()
        self.ui.statusBar.addPermanentWidget(self.memory_usage_label)

        self.ui.menuOpenRecent.aboutToShow.connect(self._populate_open_recent)

        self.toolbox_button = ToolboxButton(self)

        self.ui.toolBar.addSeparator()
        self.ui.toolBar.addWidget(self.toolbox_button)

        # Initialize dock manager. Because the parent parameter is a QMainWindow
        # the dock manager registers itself as the central widget.
        LayoutManager(self, self.ui.menuView)

        self.ui.menuStyle.addAction("Default").triggered.connect(lambda: self._set_style("default"))
        self.ui.menuStyle.addAction("TSE Light").triggered.connect(lambda: self._set_style("tse-light"))
        # self.ui.menuStyle.addAction("TSE Dark").triggered.connect(lambda: self.set_style("tse-dark"))

        LayoutManager.set_central_widget()

        datasets_dock_widget = LayoutManager.register_dock_widget(
            DatasetsWidget(
                self,
                self.toolbox_button,
                self.ui.actionPipelineEditor,
            ),
            "Datasets",
            QIcon(":/icons/datasets.png"),
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

        self.ui.actionImportDataset.triggered.connect(self._import_dataset_dialog)
        self.ui.actionNewWorkspace.triggered.connect(self._new_workspace)
        self.ui.actionOpenWorkspace.triggered.connect(self._load_workspace_dialog)
        self.ui.actionSaveWorkspace.triggered.connect(self._save_workspace_dialog)
        self.ui.actionPipelineEditor.triggered.connect(self._show_pipeline_editor)
        self.ui.actionSaveLayout.triggered.connect(self._save_layout)
        self.ui.actionRestoreLayout.triggered.connect(self._restore_layout)
        self.ui.actionResetLayout.triggered.connect(self._reset_layout)
        self.ui.actionExit.triggered.connect(lambda: QApplication.exit())
        self.ui.actionHelp.triggered.connect(self._show_help)
        self.ui.actionAbout.triggered.connect(self._show_about_dialog)
        self.ui.actionSettings.triggered.connect(self._show_settings_dialog)
        self.ui.actionExportMergedCsv.triggered.connect(self._show_export_merged_csv_dialog)

        self.ui.menuFile.aboutToShow.connect(self._menu_file_about_to_show)

        # Store default dock layout
        LayoutManager.add_perspective("Default")

        self._load_settings()

        Toast.setPositionRelativeToWidget(self)
        Toast.setMovePositionWithWidget(True)
        self.toast = None

    def _set_style(self, name: str) -> None:
        style_file = f"_internal/styles/qss/{name}.css" if IS_RELEASE else f"styles/qss/{name}.css"
        with open(style_file) as file:
            # Set global stylesheet
            QApplication.instance().setStyleSheet(file.read())
        self.settings.setValue("appStyle", name)

    def _menu_file_about_to_show(self):
        dataset = manager.get_selected_dataset()
        self.ui.actionExportMergedCsv.setVisible(dataset is not None and isinstance(dataset, IntelliMazeDataset))

    def _populate_open_recent(self):
        # Step 1. Remove the old options from the menu
        self.ui.menuOpenRecent.clear()
        # Step 2. Dynamically create the actions
        actions = []
        filenames = list(self.settings.value("recentFilesList", []))
        for filename in filenames:
            action = QAction(filename, self)
            action.triggered.connect(partial(self._load_workspace, filename))
            actions.append(action)
        # Step 3. Add the actions to the menu
        self.ui.menuOpenRecent.addActions(actions)

    def _load_workspace(self, filename: str):
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

    def _load_settings(self):
        self.restoreGeometry(self.settings.value("MainWindow/Geometry"))
        self.restoreState(self.settings.value("MainWindow/State"))

        state = self.settings.value("MainWindow/DockingState")
        if state is not None:
            LayoutManager.restore_state(state)

    def _save_settings(self):
        self.settings.setValue("MainWindow/Geometry", self.saveGeometry())
        self.settings.setValue("MainWindow/State", self.saveState())
        self.settings.setValue("MainWindow/DockingState", LayoutManager.save_state())

    def _new_workspace(self) -> None:
        if (
            QMessageBox.question(
                self,
                "TSE Analytics",
                "Do you want to clear the current workspace?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            LayoutManager.clear_dock_manager()
            manager.new_workspace()

    def _load_workspace_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Workspace",
            "",
            "Workspace Files (*.workspace)",
        )
        if file_path:
            self._load_workspace(file_path)

    def _save_workspace_dialog(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save TSE Analytics Workspace", "", "Workspace Files (*.workspace)"
        )
        if filename:
            manager.save_workspace(filename)

    def _update_memory_usage(self) -> None:
        # return the memory usage in MB
        mem = self.process.memory_info()[0] / float(2**20)
        self.memory_usage_label.setText(f"Memory usage: {mem:.2f} Mb")

    def _reset_layout(self) -> None:
        LayoutManager.open_perspective("Default")

    def _show_pipeline_editor(self):
        widget = PipelineEditorWidget()
        LayoutManager.add_widget_to_central_area(
            manager.get_selected_dataset(), widget, "Pipeline Editor", QIcon(":/icons/icons8-genealogy-16.png")
        )

    def _show_about_dialog(self) -> None:
        dialog = AboutDialog(self)
        dialog.show()

    def _show_settings_dialog(self) -> None:
        dialog = SettingsDialog(self)
        dialog.show()

    def _show_export_merged_csv_dialog(self) -> None:
        dialog = ExportMergedCsvDialog(manager.get_selected_dataset(), self)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.exec()

    def _show_help(self) -> None:
        help_mode = self.settings.value("HelpMode", "online")
        if help_mode == "online":
            help_manager.show_online_help()
        else:
            help_manager.show_offline_help()

    def _import_dataset_dialog(self) -> None:
        filter = (
            "Data Files (*.tse *.csv *.zip);;TSE Datasets (*.tse);;CSV Files (*.csv);;IntelliMaze Datasets (*.zip)"
            if CSV_IMPORT_ENABLED
            else "Data Files (*.tse *.zip);;TSE Datasets (*.tse);;IntelliMaze Datasets (*.zip)"
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

                            worker = Worker(import_intellimaze_dataset, path)
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
            manager.add_dataset(dataset)

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
            self._save_settings()
            LayoutManager.delete_dock_manager()
            help_manager.close_help_server()
            QApplication.closeAllWindows()
            super().closeEvent(event)
        else:
            event.ignore()
