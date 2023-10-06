import os
import timeit
from multiprocessing import Pool
from typing import Optional

from loguru import logger
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QIcon, QCloseEvent, QKeyEvent
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.core.notificator import show_notification
from tse_analytics.core.workers.worker import Worker
from tse_analytics.views.calo_details.calo_details_bin_selector import CaloDetailsBinSelector
from tse_analytics.views.calo_details.calo_details_box_selector import CaloDetailsBoxSelector
from tse_analytics.views.calo_details.calo_details_dialog_ui import Ui_CaloDetailsDialog
from tse_datatools.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_analytics.views.calo_details.calo_details_plot_widget import CaloDetailsPlotWidget
from tse_analytics.views.calo_details.calo_details_rer_widget import CaloDetailsRerWidget
from tse_datatools.calo_details.calo_details_processor import process_box
from tse_datatools.calo_details.calo_details_settings import get_default_settings
from tse_analytics.views.calo_details.calo_details_settings_widget import CaloDetailsSettingsWidget
from tse_analytics.views.calo_details.calo_details_table_view import CaloDetailsTableView
from tse_analytics.views.calo_details.calo_details_test_fit_widget import CaloDetailsTestFitWidget
from tse_datatools.calo_details.fitting_params import FittingParams
from tse_datatools.data.calo_details import CaloDetails
from tse_datatools.data.calo_details_box import CaloDetailsBox


class CaloDetailsDialog(QDialog):
    """CaloDetails Dialog"""

    def __init__(self, calo_details: CaloDetails, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.ui = Ui_CaloDetailsDialog()
        self.ui.setupUi(self)

        settings = QSettings()
        self.restoreGeometry(settings.value("CaloDetailsDialog/Geometry"))

        self.calo_details = calo_details

        self.calo_details_table_view = CaloDetailsTableView()
        self.calo_details_table_view.set_data(calo_details.raw_df)
        self.ui.tabWidget.addTab(self.calo_details_table_view, "Data")

        self.calo_details_plot_widget = CaloDetailsPlotWidget()
        self.calo_details_plot_widget.set_variables(calo_details.variables)
        # self.calo_details_plot_widget.set_data(calo_details.raw_df)
        self.ui.tabWidget.addTab(self.calo_details_plot_widget, "Plot")

        self.ui.toolBox.removeItem(0)

        self.ui.toolButtonCalculate.clicked.connect(self.__calculate)
        self.ui.toolButtonResetSettings.clicked.connect(self.__reset_settings)

        self.calo_details_box_selector = CaloDetailsBoxSelector(self.__filter_boxes)
        self.calo_details_box_selector.set_data(calo_details.dataset)
        self.ui.toolBox.addItem(self.calo_details_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")

        self.calo_details_bin_selector = CaloDetailsBinSelector(self.__filter_bins)
        self.calo_details_bin_selector.set_data(calo_details.dataset)
        self.ui.toolBox.addItem(self.calo_details_bin_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Bins")

        try:
            calo_details_settings = settings.value("CaloDetailsSettings", get_default_settings())
        except:
            calo_details_settings = get_default_settings()

        self.calo_details_settings_widget = CaloDetailsSettingsWidget()
        self.calo_details_settings_widget.set_settings(calo_details_settings)
        self.calo_details_settings_widget.set_data(self.calo_details.dataset)
        self.ui.toolBox.addItem(self.calo_details_settings_widget, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.calo_details_test_fit_widget = CaloDetailsTestFitWidget(self.calo_details_settings_widget)
        self.ui.tabWidget.addTab(self.calo_details_test_fit_widget, "Test")

        self.calo_details_rer_widget = CaloDetailsRerWidget()
        self.ui.tabWidget.addTab(self.calo_details_rer_widget, "RER")

        self.ui.splitter.setStretchFactor(0, 3)

        self.selected_boxes: list[CaloDetailsBox] = []
        self.selected_bins: list[int] = []

        self.fitting_results: dict[int, CaloDetailsFittingResult] = {}

    def __filter_boxes(self, selected_boxes: list[CaloDetailsBox]):
        self.selected_boxes = selected_boxes
        self.__filter()

        if len(selected_boxes) == 1:
            if selected_boxes[0].box in self.fitting_results:
                self.calo_details_rer_widget.set_data(self.fitting_results[selected_boxes[0].box])
            else:
                self.calo_details_rer_widget.clear()

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

    def __reset_settings(self):
        calo_details_settings = get_default_settings()
        self.calo_details_settings_widget.set_settings(calo_details_settings)

    def __calculate(self):
        # Pass the function to execute
        worker = Worker(self.__run_calculate)  # Any other args, kwargs are passed to the run function
        # Execute
        Manager.threadpool.start(worker)

    def __run_calculate(self):
        calo_details_settings = self.calo_details_settings_widget.get_calo_details_settings()

        # remove last bin
        bin_numbers = sorted(self.calo_details.raw_df["Bin"].unique().tolist())
        raw_df = self.calo_details.raw_df.loc[self.calo_details.raw_df["Bin"] != bin_numbers[-1]]
        active_df = self.calo_details.dataset.active_df.loc[
            self.calo_details.dataset.active_df["Bin"] != bin_numbers[-1]
        ]

        fitting_params_list: list[FittingParams] = []

        for calo_details_box in self.selected_boxes:
            # skip analysis of reference boxes
            if calo_details_box.ref_box is None:
                continue

            general_df = active_df[active_df["Box"] == calo_details_box.box].copy()
            details_df = raw_df[raw_df["Box"] == calo_details_box.box].copy()
            ref_details_df = raw_df[raw_df["Box"] == calo_details_box.ref_box].copy()

            params = FittingParams(calo_details_box, general_df, details_df, ref_details_df, calo_details_settings)
            fitting_params_list.append(params)

        self.fitting_results.clear()
        # create the process pool
        processes = len(self.selected_boxes) if len(self.selected_boxes) < os.cpu_count() else os.cpu_count()
        tic = timeit.default_timer()
        with Pool(processes=processes) as pool:
            # # issue many tasks asynchronously to the process pool
            # self.fitting_results = [pool.apply_async(calo_details_calculation_task, (params,), callback=progress) for params in fitting_params_list]
            # # close the pool
            # pool.close()
            # # wait for all issued tasks to complete
            # pool.join()

            # call the same function with different data in parallel
            for result in pool.map(process_box, fitting_params_list):
                # report the value to show progress
                self.fitting_results[result.box_number] = result

        logger.info(f"Processing complete: {timeit.default_timer() - tic} sec")
        show_notification("Calo Details", "Processing complete.")

    def hideEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("CaloDetailsDialog/Geometry", self.saveGeometry())

        calo_details_settings = self.calo_details_settings_widget.get_calo_details_settings()
        settings.setValue("CaloDetailsSettings", calo_details_settings)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
