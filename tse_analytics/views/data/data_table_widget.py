import numpy as np
import pandas as pd
from pyqttoast import ToastPreset
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.models.pandas_model import PandasModel
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.css import style_descriptive_table
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.data.data_table_widget_ui import Ui_DataTableWidget


class DataTableWidget(QWidget, messaging.MessengerListener):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_DataTableWidget()
        self.ui.setupUi(self)

        messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
        messaging.subscribe(self, messaging.DataChangedMessage, self._on_data_changed)

        self.ui.tableWidgetVariables.set_selection_mode(QAbstractItemView.SelectionMode.MultiSelection)
        self.ui.tableWidgetVariables.itemSelectionChanged.connect(self._variables_selection_changed)

        self.ui.radioButtonSplitTotal.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByAnimal.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByFactor.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByRun.toggled.connect(self._split_mode_toggled)

        self.ui.pushButtonResizeColumns.clicked.connect(self._resize_columns_width)
        self.ui.factorSelector.currentTextChanged.connect(self._factor_changed)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        self.ui.tableView.horizontalHeader().sectionClicked.connect(self._header_clicked)

        self.ui.textEditDescriptiveStats.document().setDefaultStyleSheet(style_descriptive_table)

        self.dataset = dataset
        self.df: pd.DataFrame | None = None
        self.ui.tableWidgetVariables.set_data(dataset.variables)
        self.ui.factorSelector.set_data(dataset.factors, add_empty_item=False)
        self._set_data()

    def _resize_columns_width(self):
        worker = Worker(
            self.ui.tableView.resizeColumnsToContents
        )  # Any other args, kwargs are passed to the run function
        TaskManager.start_task(worker)

    def _on_binning_applied(self, message: messaging.BinningMessage):
        if message.dataset == self.dataset:
            self._set_data()

    def _on_data_changed(self, message: messaging.DataChangedMessage):
        if message.dataset == self.dataset:
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
        if self.dataset is None:
            return

        selected_variables = self.ui.tableWidgetVariables.get_selected_variables_dict()
        split_mode = self._get_split_mode()
        selected_factor_name = self.ui.factorSelector.currentText()

        if (
            self.dataset.binning_settings.apply
            and self.dataset.binning_settings.mode != BinningMode.INTERVALS
            and split_mode != SplitMode.ANIMAL
            and len(selected_variables) == 0
        ):
            make_toast(
                self,
                "Data Table",
                "Please select at least one variable.",
                duration=4000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        if split_mode == SplitMode.FACTOR and selected_factor_name == "":
            make_toast(
                self,
                "Data Table",
                "Please select factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        self.df = self.dataset.get_data_table_df(
            variables=selected_variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
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

        self.ui.tableView.setModel(PandasModel(self.df, self.dataset, calculate=True))
        self.ui.tableView.horizontalHeader().setSortIndicatorShown(False)

    def _header_clicked(self, logical_index: int):
        if self.df is None:
            return
        self.ui.tableView.horizontalHeader().setSortIndicatorShown(True)
        order = self.ui.tableView.horizontalHeader().sortIndicatorOrder() == Qt.SortOrder.AscendingOrder
        df = self.df.sort_values(self.df.columns[logical_index], ascending=order, inplace=False)
        self.ui.tableView.setModel(PandasModel(df, self.dataset, calculate=True))

    def _add_report(self):
        content = self.ui.textEditDescriptiveStats.document().toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, content, self.dataset))
