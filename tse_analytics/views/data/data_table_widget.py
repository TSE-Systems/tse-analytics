import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import Factor, GroupingMode
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import (
    BinningMessage,
    DataChangedMessage,
    DatasetChangedMessage,
)
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.core.models.pandas_model import PandasModel
from tse_analytics.core.workers.worker import Worker
from tse_analytics.views.data.data_table_widget_ui import Ui_DataTableWidget


class DataTableWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_DataTableWidget()
        self.ui.setupUi(self)

        self.ui.pushButtonResizeColumns.clicked.connect(self.__resize_columns_width)
        self.ui.factorSelector.currentTextChanged.connect(self.__factor_changed)

        self.header = self.ui.tableView.horizontalHeader()
        self.header.sectionClicked.connect(self.header_clicked)

        self.df: pd.DataFrame | None = None
        self.selected_factor: Factor | None = None

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, BinningMessage, self.__on_binning_applied)
        messenger.subscribe(self, DataChangedMessage, self.__on_data_changed)

    def __resize_columns_width(self):
        worker = Worker(
            self.ui.tableView.resizeColumnsToContents
        )  # Any other args, kwargs are passed to the run function
        Manager.threadpool.start(worker)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.ui.tableView.setModel(None)
            self.ui.factorSelector.clear()
            self.selected_factor = None
            self.df = None
        else:
            self.ui.factorSelector.set_data(message.data.factors)
            self.__set_data()

    def __on_binning_applied(self, message: BinningMessage):
        self.ui.factorSelector.setEnabled(message.params.apply)
        self.__set_data()

    def __on_data_changed(self, message: DataChangedMessage):
        self.__set_data()

    def __factor_changed(self, selected_factor_name: str):
        factor = Manager.data.selected_dataset.factors[selected_factor_name] if selected_factor_name != "" else None
        self.selected_factor = factor
        self.__set_data()

    def __set_data(self):
        selected_variable_names = [item.name for item in Manager.data.selected_variables]
        selected_variable_names = list(set(selected_variable_names))

        self.df = Manager.data.get_data_view_df(
            variables=selected_variable_names,
            grouping_mode=GroupingMode.ANIMALS if self.selected_factor is None else GroupingMode.FACTORS,
            selected_factor=self.selected_factor,
            dropna=False,
        )

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
