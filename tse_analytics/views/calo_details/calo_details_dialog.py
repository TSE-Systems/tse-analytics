from typing import Optional
from multiprocessing import Pool

import pandas as pd
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.calo_details.calo_details_bin_selector import CaloDetailsBinSelector
from tse_analytics.views.calo_details.calo_details_box_selector import CaloDetailsBoxSelector
from tse_analytics.views.calo_details.calo_details_dialog_ui import Ui_CaloDetailsDialog
from tse_analytics.views.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_analytics.views.calo_details.calo_details_plot_widget import CaloDetailsPlotWidget
from tse_analytics.views.calo_details.calo_details_processor import calo_details_calculation_task
from tse_analytics.views.calo_details.calo_details_settings_widget import CaloDetailsSettingsWidget
from tse_analytics.views.calo_details.calo_details_table_view import CaloDetailsTableView
from tse_analytics.views.calo_details.calo_details_test_fit_widget import CaloDetailsTestFitWidget
from tse_analytics.views.calo_details.fitting_params import FittingParams
from tse_datatools.data.calo_details import CaloDetails
from tse_datatools.data.calo_details_box import CaloDetailsBox


class CaloDetailsDialog(QDialog):
    """CaloDetails Dialog"""

    def __init__(self, calo_details: CaloDetails, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.ui = Ui_CaloDetailsDialog()
        self.ui.setupUi(self)

        self.calo_details = calo_details

        self.calo_details_table_view = CaloDetailsTableView()
        self.calo_details_table_view.set_data(calo_details.raw_df)
        self.ui.tabWidget.addTab(self.calo_details_table_view, "Data")

        self.calo_details_plot_widget = CaloDetailsPlotWidget()
        self.calo_details_plot_widget.set_variables(calo_details.variables)
        # self.calo_details_plot_widget.set_data(calo_details.raw_df)
        self.ui.tabWidget.addTab(self.calo_details_plot_widget, "Plot")

        self.ui.toolBox.removeItem(0)

        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.calo_details_box_selector = CaloDetailsBoxSelector(self.__filter_boxes)
        self.calo_details_box_selector.set_data(calo_details.dataset)
        self.ui.toolBox.addItem(self.calo_details_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")

        self.calo_details_bin_selector = CaloDetailsBinSelector(self.__filter_bins)
        self.calo_details_bin_selector.set_data(calo_details.dataset)
        self.ui.toolBox.addItem(self.calo_details_bin_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Bins")

        self.calo_details_settings_widget = CaloDetailsSettingsWidget()
        self.calo_details_settings_widget.set_data(self.calo_details.dataset)
        self.ui.toolBox.addItem(self.calo_details_settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.calo_details_test_fit_widget = CaloDetailsTestFitWidget(self.calo_details_settings_widget)
        self.ui.tabWidget.addTab(self.calo_details_test_fit_widget, "Test")

        self.ui.splitter.setStretchFactor(0, 3)

        self.selected_boxes: list[CaloDetailsBox] = []
        self.selected_bins: list[int] = []

    def __filter_boxes(self, selected_boxes: list[CaloDetailsBox]):
        self.selected_boxes = selected_boxes
        self.__filter()

    def __filter_bins(self, selected_bins: list[int]):
        self.selected_bins = selected_bins
        self.__filter()

    def __filter(self):
        df = self.calo_details.raw_df

        if len(self.selected_boxes) > 0:
            box_numbers = [b.box for b in self.selected_boxes]
            df = df[df["Box"].isin(box_numbers)]

        if len(self.selected_bins) > 0:
            df = df[df["Bin"].isin(self.selected_bins)]

        self.calo_details_table_view.set_data(df)
        self.calo_details_plot_widget.set_data(df)
        self.calo_details_test_fit_widget.set_data(df)

    def __analyze(self):
        calo_details_settings = self.calo_details_settings_widget.get_calo_details_settings()

        fitting_params_list: list[FittingParams] = []

        for calo_details_box in self.selected_boxes:
            # skip analysis of reference boxes
            if calo_details_box.ref_box is None:
                continue

            general_df = self.calo_details.dataset.active_df[self.calo_details.dataset.active_df["Box"] == calo_details_box.box].copy()
            details_df = self.calo_details.raw_df[self.calo_details.raw_df["Box"] == calo_details_box.box].copy()
            ref_details_df = self.calo_details.raw_df[self.calo_details.raw_df["Box"] == calo_details_box.ref_box].copy()

            params = FittingParams(
                calo_details_box,
                general_df,
                details_df,
                ref_details_df,
                calo_details_settings
            )
            fitting_params_list.append(params)

        results: list[CaloDetailsFittingResult] = []
        # create the process pool
        with Pool() as pool:
            # call the same function with different data in parallel
            for result in pool.map(calo_details_calculation_task, fitting_params_list):
                # report the value to show progress
                results.append(result)

        measured = {}
        predicted = {}
        for result in results:
            name = result.name
            if name not in measured:
                measured[name] = []
            if name not in predicted:
                predicted[name] = []
            measured[name].extend(result.measured)
            predicted[name].extend(result.rer)

        total_measured = measured[list(measured.keys())[0]]

        rer_df = pd.DataFrame(data={"Measured": total_measured})

        for name in predicted.keys():
            rer_df[name] = predicted[name]
