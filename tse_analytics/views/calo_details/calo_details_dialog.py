from typing import Optional

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QWidget

from tse_analytics.views.calo_details.calo_details_box_selector import CaloDetailsBoxSelector
from tse_analytics.views.calo_details.calo_details_dialog_ui import Ui_CaloDetailsDialog
from tse_analytics.views.calo_details.calo_details_plot_widget import CaloDetailsPlotWidget
from tse_analytics.views.calo_details.calo_details_table_view import CaloDetailsTableView
from tse_datatools.data.box import Box
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

        self.calo_details_box_selector = CaloDetailsBoxSelector(self.__filter_boxes)
        self.calo_details_box_selector.set_data(calo_details.dataset)
        self.ui.toolBox.removeItem(0)
        self.ui.toolBox.addItem(self.calo_details_box_selector, QIcon(":/icons/icons8-dog-tag-16.png"), "Boxes")

    def __filter_boxes(self, selected_boxes: list[Box]):
        df = self.calo_details.raw_df
        if len(selected_boxes) > 0:
            box_ids = [box.id for box in selected_boxes]
            df = df[df["Box"].isin(box_ids)]
        self.calo_details_table_view.set_data(df)
        self.calo_details_plot_widget.set_data(df)
