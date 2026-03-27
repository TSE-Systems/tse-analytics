from dataclasses import dataclass, field

import pandas as pd
from pyqttoast import ToastPreset
from PySide6.QtCore import QByteArray, QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QSplitter,
    QTableView,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from tse_analytics.core import manager, messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.models.pandas_model import PandasModel
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_great_table, get_h_spacer_widget, get_widget_tool_button
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.toolbox.data_table.table_processor.table_processor_dialog import TableProcessorDialog
from tse_analytics.toolbox.data_table.variables.variables_widget import VariablesWidget
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.report_edit import ReportEdit


@dataclass
class DataWidgetSettings:
    group_by: str = "Animal"
    selected_variables: list[str] = field(default_factory=list)
    splitter_state: QByteArray | None = None


@toolbox_plugin(category="Data", label="Table", icon=":/icons/table.png", order=0)
class DataTableWidget(QWidget, messaging.MessengerListener):
    def __init__(self, datatable: Datatable, name: str = "DataTableWidget", parent: QWidget | None = None):
        super().__init__(parent)

        self.name = name
        self.datatable = datatable
        self.df: pd.DataFrame | None = None

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: DataWidgetSettings = settings.value(f"{self.name}Settings", DataWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(
            toolbar,
            self.datatable,
            check_binning=True,
            selected_mode=self._settings.group_by,
        )
        self.group_by_selector.currentTextChanged.connect(self.refresh_data)
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
        export_menu.addAction("Export to CSV...").triggered.connect(self._export_csv)
        export_menu.addAction("Export to Excel...").triggered.connect(self._export_excel)
        self.export_button.setMenu(export_menu)

        toolbar.addWidget(self.export_button)

        # Horizontal spacer
        toolbar.addWidget(get_h_spacer_widget(toolbar))

        self.descriptive_stats_widget = ReportEdit(toolbar)
        self.descriptive_stats_widget.setMinimumWidth(600)

        self.show_stats_button = get_widget_tool_button(
            toolbar,
            self.descriptive_stats_widget,
            "Descriptive Statistics",
            QIcon(":/icons/icons8-stats-16.png"),
        )
        self.show_stats_button.setEnabled(False)
        toolbar.addWidget(self.show_stats_button)

        self.add_report_action = toolbar.addAction("Add Report")
        self.add_report_action.triggered.connect(self._add_report)
        self.add_report_action.setEnabled(False)

        self.add_derived_table_action = toolbar.addAction("Add Derived Table")
        self.add_derived_table_action.triggered.connect(self._add_derived_table)

        self._layout.addWidget(toolbar)

        self._splitter = QSplitter(
            orientation=Qt.Orientation.Horizontal,
            opaqueResize=False,
            handleWidth=5,
            childrenCollapsible=True,
        )
        self._layout.addWidget(self._splitter)

        self.table_view = QTableView(
            self,
            sortingEnabled=True,
        )
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table_view.verticalHeader().setMinimumSectionSize(20)
        self.table_view.verticalHeader().setDefaultSectionSize(20)
        self.table_view.horizontalHeader().sectionClicked.connect(self._header_clicked)
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self._show_context_menu)

        self._splitter.addWidget(self.table_view)

        self.variables_widget = VariablesWidget(self)
        self.variables_widget.blockSignals(True)
        self.variables_widget.set_data(self.datatable, self._settings.selected_variables)
        self.variables_widget.tableView.selectionModel().selectionChanged.connect(self._variables_selection_changed)
        self.variables_widget.blockSignals(False)

        self._splitter.addWidget(self.variables_widget)

        self._splitter.restoreState(self._settings.splitter_state)

        self.refresh_data()

        messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
        messaging.subscribe(self, messaging.DataChangedMessage, self._on_data_changed)

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
            self.refresh_data()

    def _on_data_changed(self, message: messaging.DataChangedMessage):
        if message.dataset == self.datatable.dataset:
            self.refresh_data()

    def _variables_selection_changed(self):
        self.refresh_data()

    def refresh_data(self):
        if self.datatable is None:
            return

        selected_variables_names = self.variables_widget.get_selected_variable_names()
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

        if split_mode == SplitMode.ANIMAL:
            all_columns = self.datatable.df.columns.tolist()
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

        # self.df = self.datatable.get_preprocessed_df_columns(columns, split_mode, selected_factor_name)
        self.df = self.datatable.get_filtered_df(columns)

        if len(selected_variables_names) > 0:
            descriptive_df = self.df[selected_variables_names].describe().T.reset_index()
            descriptive = get_great_table(
                descriptive_df,
                "Descriptive Statistics",
                decimals=3,
                rowname_col="index" if "index" in descriptive_df.columns else None,
            ).as_raw_html(inline_css=True)
            self.descriptive_stats_widget.set_content(descriptive)
            self.add_report_action.setEnabled(True)
            self.show_stats_button.setEnabled(True)
        else:
            self.descriptive_stats_widget.clear()
            self.add_report_action.setEnabled(False)
            self.show_stats_button.setEnabled(False)

        self.table_view.setModel(PandasModel(self.df, self.datatable))
        self.table_view.horizontalHeader().setSortIndicatorShown(False)

    def _header_clicked(self, logical_index: int):
        if self.df is None:
            return
        self.table_view.horizontalHeader().setSortIndicatorShown(True)
        order = self.table_view.horizontalHeader().sortIndicatorOrder() == Qt.SortOrder.AscendingOrder
        df = self.df.sort_values(self.df.columns[logical_index], ascending=order, inplace=False)
        self.table_view.setModel(PandasModel(df, self.datatable))

    def _show_context_menu(self, pos) -> None:
        index = self.table_view.indexAt(pos)
        if not index.isValid():
            return

        selected = self.table_view.selectionModel().selectedIndexes()
        if not selected:
            return

        menu = QMenu(self.table_view)
        delete_values_action = menu.addAction("Delete Selected Values")
        action = menu.exec(self.table_view.viewport().mapToGlobal(pos))

        if action is None:
            return
        if action == delete_values_action:
            if (
                QMessageBox.question(
                    self,
                    "Delete Values",
                    "Are you sure you want to delete selected values? This action cannot be undone.",
                )
                == QMessageBox.StandardButton.Yes
            ):
                model = self.table_view.model()
                for idx in selected:
                    model.setData(idx, pd.NA, Qt.ItemDataRole.EditRole)

    def _add_derived_table(self):
        dialog = TableProcessorDialog(self.datatable, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pass
        dialog.deleteLater()

    def _add_report(self):
        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text="Descriptive Statistics",
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.datatable.dataset,
                    name,
                    self.descriptive_stats_widget.toHtml(),
                )
            )

    def _destroyed(self):
        messaging.unsubscribe_all(self)
        settings = QSettings()
        settings.setValue(
            f"{self.name}Settings",
            DataWidgetSettings(
                self.group_by_selector.currentText(),
                self.variables_widget.get_selected_variable_names(),
                self._splitter.saveState(),
            ),
        )
