from typing import Optional

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.messaging.messages import (
    DatasetChangedMessage,
    BinningAppliedMessage,
    RevertBinningMessage,
    DataChangedMessage,
    GroupingModeChangedMessage,
)
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.models.pandas_model import PandasModel
from tse_analytics.views.data.data_table_widget_ui import Ui_DataTableWidget


class DataTableWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_DataTableWidget()
        self.ui.setupUi(self)

        self.ui.toolButtonResizeColumns.clicked.connect(self.__resize_columns_width)

        self.header = self.ui.tableView.horizontalHeader()
        self.header.sectionClicked.connect(self.header_clicked)

        self.df: Optional[pd.DataFrame] = None

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, BinningAppliedMessage, self.__on_binning_applied)
        messenger.subscribe(self, RevertBinningMessage, self.__on_revert_binning)
        messenger.subscribe(self, DataChangedMessage, self.__on_data_changed)
        messenger.subscribe(self, GroupingModeChangedMessage, self.__on_grouping_mode_changed)

    def __resize_columns_width(self):
        # Pass the function to execute
        worker = Worker(
            self.ui.tableView.resizeColumnsToContents
        )  # Any other args, kwargs are passed to the run function
        # Execute
        Manager.threadpool.start(worker)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.ui.tableView.setModel(None)
        else:
            self.__set_data()

    def __on_binning_applied(self, message: BinningAppliedMessage):
        self.__set_data()

    def __on_revert_binning(self, message: RevertBinningMessage):
        self.__set_data()

    def __on_data_changed(self, message: DataChangedMessage):
        self.__set_data()

    def __on_grouping_mode_changed(self, message: GroupingModeChangedMessage):
        self.__set_data()

    def __set_data(self):
        selected_variable_names = [item.name for item in Manager.data.selected_variables]
        selected_variable_names = list(set(selected_variable_names))

        self.df = Manager.data.get_current_df(calculate_error=False, variables=selected_variable_names)

        self.ui.tableView.setModel(PandasModel(self.df))
        self.ui.tableView.setColumnWidth(0, 120)
        self.header.setSortIndicatorShown(False)

    def header_clicked(self, logical_index: int):
        if self.df is None:
            return
        self.header.setSortIndicatorShown(True)
        order = self.header.sortIndicatorOrder() == Qt.SortOrder.AscendingOrder
        df = self.df.sort_values(self.df.columns[logical_index], ascending=order, inplace=False)
        self.ui.tableView.setModel(PandasModel(df))
