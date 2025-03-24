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
    QToolButton,
    QMenu,
    QFileDialog,
)
from pyqttoast import ToastPreset

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.utils import get_widget_tool_button, get_h_spacer_widget
from tse_analytics.core.models.pandas_model import PandasModel
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.misc.split_mode_selector import SplitModeSelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


class DataTableWidget(QWidget, messaging.MessengerListener):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.datatable = datatable
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
        self.variables_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.variables_table_widget.itemSelectionChanged.connect(self._variables_selection_changed)
        self.variables_table_widget.set_data(self.datatable.variables)
        self.variables_table_widget.setMaximumHeight(400)
        self.variables_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        variables_button = get_widget_tool_button(
            toolbar,
            self.variables_table_widget,
            "Variables",
            QIcon(":/icons/variables.png"),
        )
        toolbar.addWidget(variables_button)

        self.split_mode_selector = SplitModeSelector(toolbar, self.datatable, self._split_mode_callback)
        toolbar.addWidget(self.split_mode_selector)

        toolbar.addSeparator()
        toolbar.addAction(QIcon(":/icons/icons8-resize-horizontal-16.png"), "Resize Columns").triggered.connect(
            self._resize_columns_width
        )

        self.export_button = QToolButton(
            popupMode=QToolButton.ToolButtonPopupMode.InstantPopup,
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.export_button.setText("Export")
        self.export_button.setIcon(QIcon(":/icons/icons8-export-16.png"))

        export_menu = QMenu("Export", self.export_button)
        export_menu.addAction("Export to CVS...").triggered.connect(self._export_csv)
        export_menu.addAction("Export to Excel...").triggered.connect(self._export_excel)
        self.export_button.setMenu(export_menu)

        toolbar.addWidget(self.export_button)

        # Horizontal spacer
        toolbar.addWidget(get_h_spacer_widget(toolbar))

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

        self.add_report_action = toolbar.addAction("Add to Report")
        self.add_report_action.triggered.connect(self._add_report)
        self.add_report_action.setEnabled(False)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.table_view = QTableView(
            self,
            sortingEnabled=True,
        )
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.verticalHeader().setMinimumSectionSize(20)
        self.table_view.verticalHeader().setDefaultSectionSize(20)
        self.table_view.horizontalHeader().sectionClicked.connect(self._header_clicked)

        self.layout.addWidget(self.table_view)

        self._set_data()

        messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
        messaging.subscribe(self, messaging.DataChangedMessage, self._on_data_changed)
        self.destroyed.connect(lambda: messaging.unsubscribe_all(self))

    def _split_mode_callback(self, mode: SplitMode, factor_name: str | None):
        self.split_mode = mode
        self.selected_factor_name = factor_name
        self._set_data()

    def _resize_columns_width(self):
        worker = Worker(
            self.table_view.resizeColumnsToContents
        )  # Any other args, kwargs are passed to the run function
        TaskManager.start_task(worker)

    def _export_csv(self):
        if self.datatable is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if filename:
            self.datatable.get_preprocessed_df().to_csv(filename, sep=";", index=False)

    def _export_excel(self):
        if self.datatable is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if filename:
            with pd.ExcelWriter(filename) as writer:
                self.datatable.get_preprocessed_df().to_excel(writer, sheet_name="Data")

    def _on_binning_applied(self, message: messaging.BinningMessage):
        if message.dataset == self.datatable.dataset:
            self._set_data()

    def _on_data_changed(self, message: messaging.DataChangedMessage):
        if message.dataset == self.datatable.dataset:
            self._set_data()

    def _variables_selection_changed(self):
        self._set_data()

    def _get_data_table_df(
        self,
        variables: dict[str, Variable],
    ) -> pd.DataFrame:
        factor_columns = list(self.datatable.dataset.factors)
        variable_columns = list(variables)
        result = self.datatable.active_df[
            self.datatable.get_default_columns() + factor_columns + variable_columns
        ].copy()

        result = self.datatable.preprocess_df(result, variables)

        # Binning
        settings = self.datatable.dataset.binning_settings
        if settings.apply:
            match settings.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        settings.time_intervals_settings,
                        variables,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        settings.time_cycles_settings,
                        variables,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        settings.time_phases_settings,
                        variables,
                    )

        # Splitting
        if (self.split_mode == SplitMode.RUN or self.split_mode == SplitMode.TOTAL) and "Bin" not in result.columns:
            make_toast(
                self,
                "Data Table",
                "Please apply binning first.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=False,
            ).show()
            return result

        result = self.datatable.process_splitting(
            result,
            self.split_mode,
            variables,
            self.selected_factor_name,
        )

        return result

    def _set_data(self):
        if self.datatable is None:
            return

        selected_variables = self.variables_table_widget.get_selected_variables_dict()
        if (
            self.datatable.dataset.binning_settings.apply
            and self.datatable.dataset.binning_settings.mode != BinningMode.INTERVALS
            and self.split_mode != SplitMode.ANIMAL
            and len(selected_variables) == 0
        ):
            make_toast(
                self,
                "Data Table",
                "Please select at least one variable.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=False,
            ).show()
            return

        if self.split_mode == SplitMode.FACTOR and self.selected_factor_name == "":
            make_toast(
                self,
                "Data Table",
                "Please select factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=False,
            ).show()
            return

        self.df = self._get_data_table_df(
            variables=selected_variables,
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

        self.table_view.setModel(PandasModel(self.df, self.datatable, calculate=True))
        self.table_view.horizontalHeader().setSortIndicatorShown(False)

    def _header_clicked(self, logical_index: int):
        if self.df is None:
            return
        self.table_view.horizontalHeader().setSortIndicatorShown(True)
        order = self.table_view.horizontalHeader().sortIndicatorOrder() == Qt.SortOrder.AscendingOrder
        df = self.df.sort_values(self.df.columns[logical_index], ascending=order, inplace=False)
        self.table_view.setModel(PandasModel(df, self.datatable, calculate=True))

    def _add_report(self):
        self.datatable.dataset.report += self.descriptive_stats_widget.document().toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
