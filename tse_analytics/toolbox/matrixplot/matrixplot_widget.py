from dataclasses import dataclass, field

from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QComboBox,
    QLabel,
    QToolBar,
    QWidget,
)

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget, get_widget_tool_button
from tse_analytics.toolbox.matrixplot.processor import MATRIXPLOT_KIND, get_matrixplot_result
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


@dataclass
class MatrixPlotWidgetSettings:
    group_by: str = "Animal"
    selected_variables: list[str] = field(default_factory=list)
    plot_type: str = "Scatter Plot"


class MatrixPlotWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        self.toast = None
        super().__init__(
            datatable,
            MatrixPlotWidgetSettings,
            title="Matrix Plot",
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

        toolbar.addWidget(QLabel("Plot Type:"))
        self.comboBoxPlotType = QComboBox(toolbar)
        self.comboBoxPlotType.addItems(MATRIXPLOT_KIND.keys())
        self.comboBoxPlotType.setCurrentText(self._settings.plot_type)
        toolbar.addWidget(self.comboBoxPlotType)

    def _get_settings_value(self):
        return MatrixPlotWidgetSettings(
            self.group_by_selector.currentText(),
            self.variables_table_widget.get_selected_variable_names(),
            self.comboBoxPlotType.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        selected_variables = self.variables_table_widget.get_selected_variables_dict()
        if len(selected_variables) < 2:
            make_toast(
                self,
                self.title,
                "Please select at least two variables.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        if split_mode == SplitMode.FACTOR and selected_factor_name == "":
            make_toast(
                self,
                self.title,
                "Please select factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        df = self.datatable.get_df(
            list(selected_variables),
            split_mode,
            selected_factor_name,
        )

        result = get_matrixplot_result(
            self.datatable.dataset,
            df,
            list(selected_variables),
            split_mode,
            selected_factor_name,
            MATRIXPLOT_KIND[self.comboBoxPlotType.currentText()],
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
