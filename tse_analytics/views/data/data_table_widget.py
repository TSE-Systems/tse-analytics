import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import SplitMode
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

        self.ui.comboBoxSplitMode.addItems(["Total", "Animal", "Run", "Factor"])
        self.ui.comboBoxSplitMode.setCurrentText("Animal")
        self.ui.comboBoxSplitMode.currentTextChanged.connect(self.__split_mode_changed)

        self.header = self.ui.tableView.horizontalHeader()
        self.header.sectionClicked.connect(self.header_clicked)

        self.df: pd.DataFrame | None = None

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
            self.df = None
        else:
            self.ui.factorSelector.set_data(message.data.factors, add_empty_item=False)
            self.__set_data()

    def __on_binning_applied(self, message: BinningMessage):
        self.__set_data()

    def __on_data_changed(self, message: DataChangedMessage):
        self.__set_data()

    def __split_mode_changed(self, split_mode_name: str):
        self.ui.factorSelector.setEnabled(split_mode_name == "Factor")
        self.__set_data()

    def __factor_changed(self, selected_factor_name: str):
        self.__set_data()

    def __set_data(self):
        if Manager.data.selected_dataset is None:
            return

        selected_variable_names = [item.name for item in Manager.data.selected_variables]
        selected_variable_names = list(set(selected_variable_names))

        selected_factor_name = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        match self.ui.comboBoxSplitMode.currentText():
            case "Animal":
                split_mode = SplitMode.ANIMAL
            case "Run":
                split_mode = SplitMode.RUN
            case "Factor":
                split_mode = SplitMode.FACTOR

        self.df = Manager.data.get_data_view_df(
            variables=selected_variable_names,
            split_mode=split_mode,
            selected_factor=selected_factor_name,
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
