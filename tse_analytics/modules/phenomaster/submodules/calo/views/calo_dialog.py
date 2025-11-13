import os
import timeit
from multiprocessing import Pool

import pandas as pd
from PySide6.QtCore import QSettings, Qt, QSize
from PySide6.QtGui import QIcon, QCloseEvent
from PySide6.QtWidgets import QDialog, QWidget, QToolBar, QMessageBox
from pyqttoast import ToastPreset

from tse_analytics.core.toaster import make_toast
from tse_analytics.modules.phenomaster.submodules.calo.fitting_result import FittingResult
from tse_analytics.modules.phenomaster.submodules.calo.processor import process_box
from tse_analytics.modules.phenomaster.submodules.calo.calo_settings import CaloSettings
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_box import CaloBox
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_data import CaloData
from tse_analytics.modules.phenomaster.submodules.calo.fitting_params import FittingParams
from tse_analytics.modules.phenomaster.submodules.calo.views.bin_selector import BinSelector
from tse_analytics.modules.phenomaster.submodules.calo.views.box_selector import BoxSelector
from tse_analytics.modules.phenomaster.submodules.calo.views.calo_dialog_ui import Ui_CaloDialog
from tse_analytics.modules.phenomaster.submodules.calo.views.plot.plot_widget import PlotWidget
from tse_analytics.modules.phenomaster.submodules.calo.views.rer.rer_widget import RerWidget
from tse_analytics.modules.phenomaster.submodules.calo.views.settings.settings_widget import (
    SettingsWidget,
)
from tse_analytics.modules.phenomaster.submodules.calo.views.test_fit.test_fit_widget import (
    TestFitWidget,
)
from tse_analytics.views.misc.pandas_widget import PandasWidget


class CaloDialog(QDialog):
    def __init__(self, calo_data: CaloData, parent: QWidget):
        super().__init__(parent)

        self.ui = Ui_CaloDialog()
        self.ui.setupUi(self)

        self.setWindowFlags(
            Qt.WindowType.Window
            # | Qt.WindowType.CustomizeWindowHint
            # | Qt.WindowType.WindowTitleHint
            # | Qt.WindowType.WindowCloseButtonHint
        )

        settings = QSettings()
        self.restoreGeometry(settings.value("CaloDialog/Geometry"))

        self.calo_data = calo_data

        self.selected_boxes: list[CaloBox] = []
        self.selected_bins: list[int] = []
        self.fitting_results: dict[int, FittingResult] = {}

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.preprocess_action = toolbar.addAction(
            QIcon(":/icons/preprocess.png"), "Calculate prediction for selected boxes"
        )
        self.preprocess_action.triggered.connect(self._calculate)
        self.reset_action = toolbar.addAction(QIcon(":/icons/icons8-undo-16.png"), "Reset settings")
        self.reset_action.triggered.connect(self._reset_settings)
        self.add_datatable_action = toolbar.addAction(
            QIcon(":/icons/icons8-insert-table-16.png"), "Append prediction to Main table"
        )
        self.add_datatable_action.setEnabled(False)
        self.add_datatable_action.triggered.connect(self._append_to_datatable)

        self.ui.verticalLayout.insertWidget(0, toolbar)

        self.calo_table_view = PandasWidget(calo_data.dataset, "Calorimetry Data")
        self.calo_table_view.set_data(calo_data.raw_df, False)
        self.ui.tabWidget.addTab(self.calo_table_view, "Data")

        self.calo_plot_widget = PlotWidget()
        self.calo_plot_widget.set_variables(calo_data.variables)
        self.ui.tabWidget.addTab(self.calo_plot_widget, "Plot")

        self.ui.toolBox.removeItem(0)

        self.calo_box_selector = BoxSelector(self._filter_boxes)
        self.calo_box_selector.set_data(calo_data.dataset)
        self.ui.toolBox.addItem(self.calo_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")

        self.calo_bin_selector = BinSelector(self._filter_bins)
        self.calo_bin_selector.set_data(calo_data.dataset)
        self.ui.toolBox.addItem(self.calo_bin_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Bins")

        try:
            calo_settings = settings.value("CaloSettings", CaloSettings.get_default())
        except Exception:
            calo_settings = CaloSettings.get_default()

        self.calo_settings_widget = SettingsWidget()
        self.calo_settings_widget.set_settings(calo_settings)
        self.calo_settings_widget.set_data(self.calo_data.dataset)
        self.ui.toolBox.addItem(self.calo_settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.calo_test_fit_widget = TestFitWidget(self.calo_settings_widget)
        self.ui.tabWidget.addTab(self.calo_test_fit_widget, "Test")

        self.calo_rer_widget = RerWidget()
        self.ui.tabWidget.addTab(self.calo_rer_widget, "RER")

        self.ui.splitter.setStretchFactor(0, 3)

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
        if (
            QMessageBox.question(self, "Reset Settings", "Do you want to reset settings to default state?")
            == QMessageBox.StandardButton.Yes
        ):
            calo_settings = CaloSettings.get_default()
            self.calo_settings_widget.set_settings(calo_settings)

    def _append_to_datatable(self):
        if len(self.fitting_results) == 0:
            return

        if (
            QMessageBox.question(self, "Append Data", "Do you want to append fitting results to Main table?")
            == QMessageBox.StandardButton.Yes
        ):
            self.calo_data.dataset.append_fitting_results(self.fitting_results)

    def _get_selected_data(self) -> pd.DataFrame:
        df = self.calo_data.raw_df

        if len(self.selected_boxes) > 0:
            box_numbers = [b.box for b in self.selected_boxes]
            df = df[df["Box"].isin(box_numbers)]

        if len(self.selected_bins) > 0:
            df = df[df["Bin"].isin(self.selected_bins)]

        return df

    def _calculate(self):
        if len(self.selected_boxes) == 0:
            return

        calo_settings = self.calo_settings_widget.get_calo_settings()

        # remove last bin
        bin_numbers = sorted(self.calo_data.raw_df["Bin"].unique().tolist())
        raw_df = self.calo_data.raw_df.loc[self.calo_data.raw_df["Bin"] != bin_numbers[-1]]
        active_df = self.calo_data.dataset.datatables["Main"].active_df.loc[
            self.calo_data.dataset.datatables["Main"].active_df["Bin"] != bin_numbers[-1]
        ]

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

        self.add_datatable_action.setEnabled(True)

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("CaloDialog/Geometry", self.saveGeometry())

        calo_settings = self.calo_settings_widget.get_calo_settings()
        settings.setValue("CaloSettings", calo_settings)
