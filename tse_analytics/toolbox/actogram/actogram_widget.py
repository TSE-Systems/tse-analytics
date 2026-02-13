from dataclasses import dataclass

from PySide6.QtWidgets import QLabel, QSpinBox, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.toolbox.actogram.processor import get_actogram_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class ActogramWidgetSettings:
    selected_variable: str = None
    bins_per_hour: int = 6


@toolbox_plugin(category="Circadian Analysis", label="Actogram", icon=":/icons/icons8-barcode-16.png", order=0)
class ActogramWidget(ToolboxWidgetBase):
    """Widget for visualizing activity patterns over time in a double-plotted actogram format.

    An actogram is a graphical representation of activity data over multiple days,
    typically used in chronobiology to visualize circadian rhythms. This widget
    creates a double-plotted actogram where each row represents two consecutive days,
    allowing for better visualization of activity patterns that cross midnight.
    """

    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            ActogramWidgetSettings,
            title="Actogram",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addWidget(QLabel("Bins per hour:"))
        self.bins_spin_box = QSpinBox(
            toolbar,
            minimum=1,
            maximum=60,
            singleStep=1,
            value=self._settings.bins_per_hour,
        )
        toolbar.addWidget(self.bins_spin_box)

    def _get_settings_value(self):
        return ActogramWidgetSettings(
            self.variableSelector.currentText(),
            self.bins_spin_box.value(),
        )

    def _update(self):
        self.report_view.clear()

        variable = self.variableSelector.get_selected_variable()

        columns = ["Animal", "DateTime", variable.name]
        df = self.datatable.get_filtered_df(columns)

        result = get_actogram_result(
            self.datatable.dataset,
            df,
            variable,
            self.bins_spin_box.value(),
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
