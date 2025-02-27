import os
import timeit
from multiprocessing import Pool

import pandas as pd
from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
from PySide6.QtWidgets import QDialog, QFileDialog, QWidget

from tse_analytics.core.toaster import make_toast
from tse_analytics.modules.phenomaster.submodules.calo.calo_fitting_result import CaloFittingResult
from tse_analytics.modules.phenomaster.submodules.calo.calo_processor import process_box
from tse_analytics.modules.phenomaster.submodules.calo.calo_settings import CaloSettings
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_data import CaloData
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_box import CaloBox
from tse_analytics.modules.phenomaster.submodules.calo.fitting_params import FittingParams
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_bin_selector import CaloBinSelector
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_box_selector import CaloBoxSelector
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_plot_widget import CaloPlotWidget
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_rer_widget import CaloRerWidget
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_settings_widget import (
    CaloSettingsWidget,
)
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_table_view import CaloTableView
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_test_fit_widget import (
    CaloTestFitWidget,
)
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_dialog_ui import Ui_CaloDialog


class CaloDialog(QDialog):
    def __init__(self, calo_data: CaloData, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_CaloDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("CaloDialog/Geometry"))

        self.calo_data = calo_data

        self.calo_table_view = CaloTableView()
        self.calo_table_view.set_data(calo_data.raw_df)
        self.ui.tabWidget.addTab(self.calo_table_view, "Data")

        self.calo_plot_widget = CaloPlotWidget()
        self.calo_plot_widget.set_variables(calo_data.variables)
        self.ui.tabWidget.addTab(self.calo_plot_widget, "Plot")

        self.ui.toolBox.removeItem(0)

        self.ui.toolButtonCalculate.clicked.connect(self._calculate)
        self.ui.toolButtonResetSettings.clicked.connect(self._reset_settings)
        self.ui.toolButtonExport.clicked.connect(self._export)

        self.calo_box_selector = CaloBoxSelector(self._filter_boxes)
        self.calo_box_selector.set_data(calo_data.dataset)
        self.ui.toolBox.addItem(self.calo_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")

        self.calo_bin_selector = CaloBinSelector(self._filter_bins)
        self.calo_bin_selector.set_data(calo_data.dataset)
        self.ui.toolBox.addItem(self.calo_bin_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Bins")

        try:
            calo_settings = settings.value("CaloSettings", CaloSettings.get_default())
        except Exception:
            calo_settings = CaloSettings.get_default()

        self.calo_settings_widget = CaloSettingsWidget()
        self.calo_settings_widget.set_settings(calo_settings)
        self.calo_settings_widget.set_data(self.calo_data.dataset)
        self.ui.toolBox.addItem(self.calo_settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.calo_test_fit_widget = CaloTestFitWidget(self.calo_settings_widget)
        self.ui.tabWidget.addTab(self.calo_test_fit_widget, "Test")

        self.calo_rer_widget = CaloRerWidget()
        self.ui.tabWidget.addTab(self.calo_rer_widget, "RER")

        self.ui.splitter.setStretchFactor(0, 3)

        self.selected_boxes: list[CaloBox] = []
        self.selected_bins: list[int] = []

        self.fitting_results: dict[int, CaloFittingResult] = {}

    def _filter_boxes(self, selected_boxes: list[CaloBox]):
        self.selected_boxes = selected_boxes
        self._filter()

        if len(selected_boxes) == 1:
            if selected_boxes[0].box in self.fitting_results:
                self.calo_rer_widget.set_data(self.fitting_results[selected_boxes[0].box])
            else:
                self.calo_rer_widget.clear()

    def _filter_bins(self, selected_bins: list[int]):
        self.selected_bins = selected_bins
        self._filter()

    def _filter(self):
        df = self._get_selected_data()

        self.calo_table_view.set_data(df)
        self.calo_plot_widget.set_data(df)
        self.calo_test_fit_widget.set_data(df)

    def _reset_settings(self):
        calo_settings = CaloSettings.get_default()
        self.calo_settings_widget.set_settings(calo_settings)

    def _export(self):
        df = self._get_selected_data()
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if filename:
            if not df.empty:
                df.to_csv(filename, sep=";", index=False)

    def _get_selected_data(self) -> pd.DataFrame:
        df = self.calo_data.raw_df

        if len(self.selected_boxes) > 0:
            box_numbers = [b.box for b in self.selected_boxes]
            df = df[df["Box"].isin(box_numbers)]

        if len(self.selected_bins) > 0:
            df = df[df["Bin"].isin(self.selected_bins)]

        return df

    def _calculate(self):
        calo_settings = self.calo_settings_widget.get_calo_settings()

        # remove last bin
        bin_numbers = sorted(self.calo_data.raw_df["Bin"].unique().tolist())
        raw_df = self.calo_data.raw_df.loc[self.calo_data.raw_df["Bin"] != bin_numbers[-1]]
        active_df = self.calo_data.dataset.active_df.loc[self.calo_data.dataset.active_df["Bin"] != bin_numbers[-1]]

        fitting_params_list: list[FittingParams] = []

        for calo_box in self.selected_boxes:
            # skip analysis of reference boxes
            if calo_box.ref_box is None:
                continue

            # TODO: check int -> str conversion for general table!
            # general_df = active_df[active_df["Box"] == str(calo_box.box)].copy()
            main_df = active_df[active_df["Box"] == calo_box.box].copy()
            box_df = raw_df[raw_df["Box"] == calo_box.box].copy()
            ref_df = raw_df[raw_df["Box"] == calo_box.ref_box].copy()

            params = FittingParams(calo_box, main_df, box_df, ref_df, calo_settings)
            fitting_params_list.append(params)

        self.fitting_results.clear()
        # create the process pool
        processes = len(self.selected_boxes) if len(self.selected_boxes) < os.cpu_count() else os.cpu_count()
        tic = timeit.default_timer()
        with Pool(processes=processes) as pool:
            # call the same function with different data in parallel
            for result in pool.map(process_box, fitting_params_list):
                # report the value to show progress
                self.fitting_results[result.box_number] = result

        make_toast(
            self,
            "Calorimetry Analysis",
            f"Processing complete in {timeit.default_timer() - tic} sec.",
            duration=4000,
            preset=ToastPreset.SUCCESS,
            show_duration_bar=True,
            echo_to_logger=True,
        ).show()

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("CaloDialog/Geometry", self.saveGeometry())

        calo_settings = self.calo_settings_widget.get_calo_settings()
        settings.setValue("CaloSettings", calo_settings)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
