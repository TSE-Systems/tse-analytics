import numpy as np
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QAbstractItemView

from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import (
    AddToReportMessage,
    BinningMessage,
    DataChangedMessage,
    DatasetChangedMessage,
)
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.core.models.pandas_model import PandasModel
from tse_analytics.core.workers.worker import Worker
from tse_analytics.css import style_descriptive_table
from tse_analytics.views.data.data_table_widget_ui import Ui_DataTableWidget


class DataTableWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_DataTableWidget()
        self.ui.setupUi(self)

        self.ui.tableWidgetVariables.set_selection_mode(QAbstractItemView.SelectionMode.MultiSelection)
        self.ui.tableWidgetVariables.itemSelectionChanged.connect(self._variables_selection_changed)

        self.ui.radioButtonSplitTotal.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByAnimal.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByFactor.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByRun.toggled.connect(self._split_mode_toggled)

        self.ui.pushButtonResizeColumns.clicked.connect(self._resize_columns_width)
        self.ui.factorSelector.currentTextChanged.connect(self._factor_changed)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        self.header = self.ui.tableView.horizontalHeader()
        self.header.sectionClicked.connect(self._header_clicked)

        self.ui.textEditDescriptiveStats.document().setDefaultStyleSheet(style_descriptive_table)

        self.df: pd.DataFrame | None = None

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, BinningMessage, self._on_binning_applied)
        messenger.subscribe(self, DataChangedMessage, self._on_data_changed)

    def _resize_columns_width(self):
        worker = Worker(
            self.ui.tableView.resizeColumnsToContents
        )  # Any other args, kwargs are passed to the run function
        Manager.threadpool.start(worker)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        if message.data is None:
            self.ui.tableView.setModel(None)
            self.ui.tableWidgetVariables.clear_data()
            self.ui.textEditDescriptiveStats.document().clear()
            self.ui.factorSelector.clear()
            self.df = None
        else:
            self.ui.tableWidgetVariables.set_data(message.data.variables)
            self.ui.factorSelector.set_data(message.data.factors, add_empty_item=False)
            self._set_data()

    def _on_binning_applied(self, message: BinningMessage):
        self._set_data()

    def _on_data_changed(self, message: DataChangedMessage):
        self._set_data()

    def _variables_selection_changed(self):
        self._set_data()

    def _get_split_mode(self) -> SplitMode:
        if self.ui.radioButtonSplitByAnimal.isChecked():
            return SplitMode.ANIMAL
        elif self.ui.radioButtonSplitByRun.isChecked():
            return SplitMode.RUN
        elif self.ui.radioButtonSplitByFactor.isChecked():
            return SplitMode.FACTOR
        else:
            return SplitMode.TOTAL

    def _split_mode_toggled(self, toggled: bool):
        if not toggled:
            return

        split_mode = self._get_split_mode()
        self.ui.factorSelector.setEnabled(split_mode == SplitMode.FACTOR)
        self._set_data()

    def _factor_changed(self, selected_factor_name: str):
        self._set_data()

    def _set_data(self):
        if Manager.data.selected_dataset is None:
            return

        selected_variables = self.ui.tableWidgetVariables.get_selected_variables_dict()
        split_mode = self._get_split_mode()
        selected_factor_name = self.ui.factorSelector.currentText()

        self.df = Manager.data.get_data_table_df(
            variables=selected_variables,
            split_mode=split_mode,
            selected_factor=selected_factor_name,
        )

        if len(selected_variables) > 0:
            selected_variable_names = selected_variables.keys()
            descriptive = (
                np.round(self.df[selected_variable_names].describe(), 3)
                .T[["count", "mean", "std", "min", "max"]]
                .to_html()
            )
            self.ui.textEditDescriptiveStats.document().setHtml(descriptive)
            self.ui.pushButtonAddReport.setEnabled(True)
        else:
            self.ui.textEditDescriptiveStats.document().clear()
            self.ui.pushButtonAddReport.setEnabled(False)

        self.ui.tableView.setModel(PandasModel(self.df, calculate=True))
        self.header.setSortIndicatorShown(False)

    def _header_clicked(self, logical_index: int):
        if self.df is None:
            return
        self.header.setSortIndicatorShown(True)
        order = self.header.sortIndicatorOrder() == Qt.SortOrder.AscendingOrder
        df = self.df.sort_values(self.df.columns[logical_index], ascending=order, inplace=False)
        self.ui.tableView.setModel(PandasModel(df, calculate=True))

    def _add_report(self):
        content = self.ui.textEditDescriptiveStats.document().toHtml()
        Manager.messenger.broadcast(AddToReportMessage(self, content))
