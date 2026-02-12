from dataclasses import dataclass, field

from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QDoubleSpinBox,
    QLabel,
    QSpinBox,
    QToolBar,
    QWidget,
)

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget, get_widget_tool_button
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.toolbox.tsne.processor import TsneResult, get_tsne_result
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


@dataclass
class TsneWidgetSettings:
    group_by: str = "Animal"
    selected_variables: list[str] = field(default_factory=list)
    perplexity: float = 30.0
    maximum_iterations: int = 1000


class TsneWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        self._toast = None
        super().__init__(
            datatable,
            TsneWidgetSettings,
            title="tSNE",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
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

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Perplexity:"))
        self.perplexity_spin_box = QDoubleSpinBox(
            toolbar,
            minimum=5,
            maximum=50,
            singleStep=1,
            value=self._settings.perplexity,
        )
        toolbar.addWidget(self.perplexity_spin_box)

        toolbar.addWidget(QLabel("Maximum Iterations:"))
        self.maximum_iterations_spin_box = QSpinBox(
            toolbar,
            minimum=250,
            maximum=10000,
            singleStep=250,
            value=self._settings.maximum_iterations,
        )
        toolbar.addWidget(self.maximum_iterations_spin_box)

    def _get_settings_value(self):
        return TsneWidgetSettings(
            self.group_by_selector.currentText(),
            self.variables_table_widget.get_selected_variable_names(),
            self.perplexity_spin_box.value(),
            self.maximum_iterations_spin_box.value(),
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
            get_tsne_result,
            self.datatable.dataset,
            df,
            selected_variables,
            split_mode,
            selected_factor_name,
            self.perplexity_spin_box.value(),
            self.maximum_iterations_spin_box.value(),
            get_figsize_from_widget(self.report_view),
        )
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _result(self, result: TsneResult):
        self.report_view.set_content(result.report)

    def _finished(self):
        self._toast.hide()
        self.update_action.setEnabled(True)
