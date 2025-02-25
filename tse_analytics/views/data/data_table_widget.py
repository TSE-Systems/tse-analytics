import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QWidget,
    QToolBar,
    QTableView,
    QVBoxLayout,
    QTextEdit,
    QAbstractScrollArea,
)
from pyqttoast import ToastPreset

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import get_widget_tool_button, get_h_spacer_widget
from tse_analytics.core.models.pandas_model import PandasModel
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.misc.split_mode_selector import SplitModeSelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


class DataTableWidget(QWidget, messaging.MessengerListener):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)

        messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
        messaging.subscribe(self, messaging.DataChangedMessage, self._on_data_changed)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.dataset = dataset
        self.df: pd.DataFrame | None = None
        self.split_mode = SplitMode.ANIMAL
        self.selected_factor_name = ""

        # Setup toolbar
        toolbar = QToolBar(
            "Data Table Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.variables_table_widget = VariablesTableWidget()
        self.variables_table_widget.set_selection_mode(QAbstractItemView.SelectionMode.MultiSelection)
        self.variables_table_widget.itemSelectionChanged.connect(self._variables_selection_changed)
        self.variables_table_widget.set_data(self.dataset.variables)
        self.variables_table_widget.setMaximumHeight(400)
        self.variables_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        variables_button = get_widget_tool_button(
            toolbar,
            self.variables_table_widget,
            "Variables",
            QIcon(":/icons/variables.png"),
        )
        toolbar.addWidget(variables_button)

        split_mode_selector = SplitModeSelector(toolbar, self.dataset.factors, self._split_mode_callback)
        toolbar.addWidget(split_mode_selector)

        self.descriptive_stats_widget = QTextEdit(toolbar)
        self.descriptive_stats_widget.setUndoRedoEnabled(False)
        self.descriptive_stats_widget.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.descriptive_stats_widget.setReadOnly(True)
        self.descriptive_stats_widget.setMinimumWidth(410)
        self.descriptive_stats_widget.document().setDefaultStyleSheet(style_descriptive_table)

        self.show_stats_button = get_widget_tool_button(
            toolbar,
            self.descriptive_stats_widget,
            "Show Descriptive Statistics",
            QIcon(":/icons/icons8-stats-16.png"),
        )
        self.show_stats_button.setEnabled(False)
        toolbar.addWidget(self.show_stats_button)

        toolbar.addSeparator()
        toolbar.addAction(QIcon(":/icons/icons8-resize-horizontal-16.png"), "Resize Columns").triggered.connect(
            self._resize_columns_width
        )

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        self.add_report_action = toolbar.addAction("Add to Report")
        self.add_report_action.triggered.connect(self._add_report)
        self.add_report_action.setEnabled(False)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.tableView = QTableView(
            self,
            sortingEnabled=True,
        )
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.verticalHeader().setMinimumSectionSize(20)
        self.tableView.verticalHeader().setDefaultSectionSize(20)
        self.tableView.horizontalHeader().sectionClicked.connect(self._header_clicked)

        self.layout.addWidget(self.tableView)

        self._set_data()

    def _split_mode_callback(self, mode: SplitMode, factor_name: str | None):
        self.split_mode = mode
        self.selected_factor_name = factor_name
        self._set_data()

    def _resize_columns_width(self):
        worker = Worker(self.tableView.resizeColumnsToContents)  # Any other args, kwargs are passed to the run function
        TaskManager.start_task(worker)

    def _on_binning_applied(self, message: messaging.BinningMessage):
        if message.dataset == self.dataset:
            self._set_data()

    def _on_data_changed(self, message: messaging.DataChangedMessage):
        if message.dataset == self.dataset:
            self._set_data()

    def _variables_selection_changed(self):
        self._set_data()

    def _set_data(self):
        if self.dataset is None:
            return

        selected_variables = self.variables_table_widget.get_selected_variables_dict()
        if (
            self.dataset.binning_settings.apply
            and self.dataset.binning_settings.mode != BinningMode.INTERVALS
            and self.split_mode != SplitMode.ANIMAL
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

        if self.split_mode == SplitMode.FACTOR and self.selected_factor_name == "":
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
            split_mode=self.split_mode,
            selected_factor_name=self.selected_factor_name,
        )

        if len(selected_variables) > 0:
            selected_variable_names = selected_variables.keys()
            descriptive = (
                np.round(self.df[selected_variable_names].describe(), 3)
                .T[["count", "mean", "std", "min", "max"]]
                .to_html()
            )
            self.descriptive_stats_widget.document().setHtml(descriptive)
            self.add_report_action.setEnabled(True)
            self.show_stats_button.setEnabled(True)
        else:
            self.descriptive_stats_widget.document().clear()
            self.add_report_action.setEnabled(False)
            self.show_stats_button.setEnabled(False)

        self.tableView.setModel(PandasModel(self.df, self.dataset, calculate=True))
        self.tableView.horizontalHeader().setSortIndicatorShown(False)

    def _header_clicked(self, logical_index: int):
        if self.df is None:
            return
        self.tableView.horizontalHeader().setSortIndicatorShown(True)
        order = self.tableView.horizontalHeader().sortIndicatorOrder() == Qt.SortOrder.AscendingOrder
        df = self.df.sort_values(self.df.columns[logical_index], ascending=order, inplace=False)
        self.tableView.setModel(PandasModel(df, self.dataset, calculate=True))

    def _add_report(self):
        self.dataset.report += self.descriptive_stats_widget.document().toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
