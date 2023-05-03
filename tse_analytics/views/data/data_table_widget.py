from typing import Optional

import pandas as pd
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.messaging.messages import ClearDataMessage, DatasetChangedMessage, BinningAppliedMessage, \
    RevertBinningMessage, DataChangedMessage, GroupingModeChangedMessage
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

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ui.tableView.setModel(proxy_model)

        self.ui.toolButtonEnableSorting.toggled.connect(self.__enable_sorting)
        self.ui.toolButtonResizeColumns.clicked.connect(self.__resize_columns_width)

        self._sorting = False

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)
        messenger.subscribe(self, BinningAppliedMessage, self.__on_binning_applied)
        messenger.subscribe(self, RevertBinningMessage, self.__on_revert_binning)
        messenger.subscribe(self, DataChangedMessage, self.__on_data_changed)
        messenger.subscribe(self, GroupingModeChangedMessage, self.__on_grouping_mode_changed)

    def __enable_sorting(self, state: bool):
        self._sorting = state
        self.ui.tableView.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self.ui.tableView.setSortingEnabled(self._sorting)

    def __resize_columns_width(self):
        # Pass the function to execute
        worker = Worker(self.ui.tableView.resizeColumnsToContents)  # Any other args, kwargs are passed to the run function
        # Execute
        Manager.threadpool.start(worker)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        df = Manager.data.get_current_df(calculate_error=False)
        self.__set_data(df)

    def __on_clear_data(self, message: ClearDataMessage):
        self.ui.tableView.model().setSourceModel(None)

    def __on_binning_applied(self, message: BinningAppliedMessage):
        df = Manager.data.get_current_df(calculate_error=False)
        self.__set_data(df)

    def __on_revert_binning(self, message: RevertBinningMessage):
        df = Manager.data.selected_dataset.active_df
        self.__set_data(df)

    def __on_data_changed(self, message: DataChangedMessage):
        df = Manager.data.get_current_df(calculate_error=False)
        self.__set_data(df)

    def __on_grouping_mode_changed(self, message: GroupingModeChangedMessage):
        df = Manager.data.get_current_df(calculate_error=False)
        self.__set_data(df)

    def __set_data(self, df: pd.DataFrame):
        selected_variable_names = [item.name for item in Manager.data.selected_variables]
        selected_variable_names = set(selected_variable_names)

        all_variable_names = Manager.data.selected_dataset.variables
        all_variable_names = set(all_variable_names)

        drop_columns = all_variable_names - selected_variable_names

        df = df.drop(columns=drop_columns)

        model = PandasModel(df)
        self.ui.tableView.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self.ui.tableView.setSortingEnabled(False)
        self.ui.tableView.model().setSourceModel(model)
        self.ui.tableView.setSortingEnabled(self._sorting)