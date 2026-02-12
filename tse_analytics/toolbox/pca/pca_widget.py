from dataclasses import dataclass, field

from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QInputDialog,
    QLabel,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget, get_h_spacer_widget, get_widget_tool_button
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.toolbox.pca.processor import PcaResult, get_pca_result
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.report_edit import ReportEdit
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


@dataclass
class PcaWidgetSettings:
    group_by: str = "Animal"
    selected_variables: list[str] = field(default_factory=list)


class PcaWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: PcaWidgetSettings = settings.value(self.__class__.__name__, PcaWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "PCA"

        self.datatable = datatable
        self._toast = None

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.update_action = toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update")
        self.update_action.triggered.connect(self._update)
        toolbar.addSeparator()

        self.variables_table_widget = VariablesTableWidget()
        self.variables_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.variables_table_widget.set_data(self.datatable.variables, self._settings.selected_variables)
        self.variables_table_widget.setMaximumHeight(600)
        self.variables_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        variables_button = get_widget_tool_button(
            toolbar,
            self.variables_table_widget,
            "Variables",
            QIcon(":/icons/variables.png"),
        )
        toolbar.addWidget(variables_button)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.report_view = ReportEdit(self)
        self._layout.addWidget(self.report_view)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add Report").triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            PcaWidgetSettings(
                self.group_by_selector.currentText(),
                self.variables_table_widget.get_selected_variable_names(),
            ),
        )

    def _update(self):
        self.report_view.clear()

        self.update_action.setEnabled(False)

        selected_variables = self.variables_table_widget.get_selected_variable_names()
        if len(selected_variables) < 3:
            make_toast(
                self,
                self.title,
                "Please select at least three variables.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        self._toast = make_toast(self, self.title, "Processing...")
        self._toast.show()

        df = self.datatable.get_df(
            selected_variables,
            split_mode,
            selected_factor_name,
        )
        df.dropna(inplace=True)

        worker = Worker(
            get_pca_result,
            self.datatable.dataset,
            df,
            selected_variables,
            split_mode,
            selected_factor_name,
            get_figsize_from_widget(self.report_view),
        )
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _result(self, result: PcaResult):
        self.report_view.set_content(result.report)

    def _finished(self):
        self._toast.hide()
        self.update_action.setEnabled(True)

    def _add_report(self):
        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text=self.title,
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.datatable.dataset,
                    name,
                    self.report_view.toHtml(),
                )
            )
