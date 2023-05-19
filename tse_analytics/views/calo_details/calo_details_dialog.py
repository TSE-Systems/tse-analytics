from typing import Optional

import pandas as pd
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.calo_details.calo_details_bin_selector import CaloDetailsBinSelector
from tse_analytics.views.calo_details.calo_details_box_selector import CaloDetailsBoxSelector
from tse_analytics.views.calo_details.calo_details_dialog_ui import Ui_CaloDetailsDialog
from tse_analytics.views.calo_details.calo_details_plot_widget import CaloDetailsPlotWidget
from tse_analytics.views.calo_details.calo_details_settings_widget import CaloDetailsSettingsWidget
from tse_analytics.views.calo_details.calo_details_table_view import CaloDetailsTableView
from tse_datatools.data.calo_details import CaloDetails


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

        self.calo_details_box_selector = CaloDetailsBoxSelector(self.__filter_boxes)
        self.calo_details_box_selector.set_data(calo_details.dataset)
        self.ui.toolBox.addItem(self.calo_details_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")

        self.calo_details_bin_selector = CaloDetailsBinSelector(self.__filter_bins)
        self.calo_details_bin_selector.set_data(calo_details.dataset)
        self.ui.toolBox.addItem(self.calo_details_bin_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Bins")

        self.calo_details_settings = CaloDetailsSettingsWidget()
        self.ui.toolBox.addItem(self.calo_details_settings, QIcon(":/icons/icons8-dog-tag-16.png"), "Settings")

        self.ui.splitter.setStretchFactor(0, 3)

        self.selected_boxes: list[int] = []
        self.selected_bins: list[int] = []

    def __filter_boxes(self, selected_boxes: list[int]):
        self.selected_boxes = selected_boxes
        self.__filter()

    def __filter_bins(self, selected_bins: list[int]):
        self.selected_bins = selected_bins
        self.__filter()

    def __filter(self):
        df = self.calo_details.raw_df

        if len(self.selected_boxes) > 0:
            df = df[df["Box"].isin(self.selected_boxes)]

        if len(self.selected_bins) > 0:
            df = df[df["Bin"].isin(self.selected_bins)]

        self.calo_details_table_view.set_data(df)
        self.calo_details_plot_widget.set_data(df)
