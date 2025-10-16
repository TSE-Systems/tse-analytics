from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, QSize, QSettings
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
    QLabel,
)
from pyqttoast import ToastPreset

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.models.pandas_model import PandasModel
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_widget_tool_button, get_h_spacer_widget
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


@dataclass
class DataTableWidgetSettings:
    group_by: str = "Animal"
    selected_variables: list[str] = field(default_factory=list)


class DataTableWidget(QWidget, messaging.MessengerListener):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Settings management
        settings = QSettings()
        self._settings: DataTableWidgetSettings = settings.value(self.__class__.__name__, DataTableWidgetSettings())
        self.destroyed.connect(
            lambda: settings.setValue(
                self.__class__.__name__,
                DataTableWidgetSettings(
                    self.group_by_selector.currentText(),
                    self.variables_table_widget.get_selected_variable_names(),
                ),
            )
        )

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.datatable = datatable
        self.df: pd.DataFrame | None = None

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.variables_table_widget = VariablesTableWidget()
        self.variables_table_widget.blockSignals(True)
        self.variables_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.variables_table_widget.itemSelectionChanged.connect(self._variables_selection_changed)
        self.variables_table_widget.set_data(self.datatable.variables, self._settings.selected_variables)
        self.variables_table_widget.setMaximumHeight(400)
        self.variables_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.variables_table_widget.blockSignals(False)

        variables_button = get_widget_tool_button(
            toolbar,
            self.variables_table_widget,
            "Variables",
            QIcon(":/icons/variables.png"),
        )
        toolbar.addWidget(variables_button)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, self._group_by_callback)
        self.group_by_selector.blockSignals(True)
        self.group_by_selector.setCurrentText(self._settings.group_by)
        self.group_by_selector.blockSignals(False)
        toolbar.addWidget(self.group_by_selector)

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
        self._layout.addWidget(toolbar)

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

        self._layout.addWidget(self.table_view)

        self._set_data()

        messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
        messaging.subscribe(self, messaging.DataChangedMessage, self._on_data_changed)
        self.destroyed.connect(lambda: messaging.unsubscribe_all(self))

    def _group_by_callback(self, mode: SplitMode, factor_name: str | None):
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
            self.df.to_csv(filename, sep=";", index=False)

    def _export_excel(self):
        if self.datatable is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "", "Excel Files (*.xlsx)")
        if filename:
            with pd.ExcelWriter(filename) as writer:
                self.df.to_excel(writer, sheet_name=self.datatable.name)

    def _on_binning_applied(self, message: messaging.BinningMessage):
        if message.dataset == self.datatable.dataset:
            self._set_data()

    def _on_data_changed(self, message: messaging.DataChangedMessage):
        if message.dataset == self.datatable.dataset:
            self._set_data()

    def _variables_selection_changed(self):
        self._set_data()

    def _set_data(self):
        if self.datatable is None:
            return

        selected_variables_names = self.variables_table_widget.get_selected_variable_names()
        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        if (
            self.datatable.dataset.binning_settings.apply
            and self.datatable.dataset.binning_settings.mode == BinningMode.PHASES
            and len(selected_variables_names) == 0
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

        # self.df = self.datatable.get_preprocessed_df(selected_variables, self.split_mode, self.selected_factor_name)

        if split_mode == SplitMode.ANIMAL:
            all_columns = self.datatable.active_df.columns.tolist()
            all_variable_columns = list(self.datatable.variables.keys())
            columns = [
                var_column for var_column in all_columns if var_column not in all_variable_columns
            ] + selected_variables_names
        else:
            columns = list(
                dict.fromkeys(
                    self.datatable.get_default_columns()
                    + self.datatable.get_categorical_columns()
                    + selected_variables_names
                )
            )

        self.df = self.datatable.get_preprocessed_df_columns(columns, split_mode, selected_factor_name)

        if len(selected_variables_names) > 0:
            descriptive = (
                np.round(self.df[selected_variables_names].describe(), 3)
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
