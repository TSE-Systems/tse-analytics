from dataclasses import dataclass, field

from pyqttoast import ToastPreset
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QLabel, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import FactorRole
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget, get_widget_tool_button
from tse_analytics.toolbox.composite_score.processor import get_composite_score_result
from tse_analytics.toolbox.composite_score.score_config_table_widget import ScoreConfigTableWidget
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.group_by_selector import GroupBySelector

_NORMALIZATION_LABELS = {"zscore": "Z-score", "minmax": "Min-max"}


@dataclass
class CompositeScoreWidgetSettings:
    selected_variables: list[str] = field(default_factory=list)
    directions: dict[str, str] = field(default_factory=dict)  # name -> "higher" | "lower"
    weights: dict[str, float] = field(default_factory=dict)  # name -> weight
    normalization: str = "zscore"  # "zscore" | "minmax"
    color_by: str = "Animal"  # factor name used to color the chart bars


@toolbox_plugin(
    category="Exploration",
    label="Composite Performance Score",
    icon=":/icons/exploration.png",
    order=3,
)
class CompositeScoreWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            CompositeScoreWidgetSettings,
            title="Composite Performance Score",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        self.config_table = ScoreConfigTableWidget()
        self.config_table.set_data(
            self.datatable.variables,
            self._settings.selected_variables,
            self._settings.directions,
            self._settings.weights,
        )
        variables_button = get_widget_tool_button(
            toolbar,
            self.config_table,
            "Variables",
            QIcon(":/icons/variables.png"),
        )
        toolbar.addWidget(variables_button)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Normalization:"))
        self.normalization_selector = QComboBox(toolbar)
        self.normalization_selector.addItems(list(_NORMALIZATION_LABELS.values()))
        self.normalization_selector.setCurrentText(_NORMALIZATION_LABELS.get(self._settings.normalization, "Z-score"))
        toolbar.addWidget(self.normalization_selector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Color by:"))
        self.color_by_selector = GroupBySelector(
            toolbar,
            self.datatable,
            selected_mode=self._settings.color_by,
            show_role=FactorRole.BETWEEN_SUBJECT,
        )
        toolbar.addWidget(self.color_by_selector)

    def _get_settings_value(self) -> CompositeScoreWidgetSettings:
        selected, directions, weights = self.config_table.get_config()
        normalization = "minmax" if self.normalization_selector.currentText() == "Min-max" else "zscore"
        return CompositeScoreWidgetSettings(
            selected_variables=selected,
            directions=directions,
            weights=weights,
            normalization=normalization,
            color_by=self.color_by_selector.currentText(),
        )

    def _update(self) -> None:
        self.report_view.clear()

        selected, directions, weights = self.config_table.get_config()
        if len(selected) < 2:
            make_toast(
                self,
                self.title,
                "Please select at least two variables.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        normalization = "minmax" if self.normalization_selector.currentText() == "Min-max" else "zscore"
        color_by = self.color_by_selector.currentText()

        result = get_composite_score_result(
            self.datatable,
            selected,
            directions,
            weights,
            normalization,
            color_by,
            get_figsize_from_widget(self.report_view),
        )

        if result is None:
            make_toast(
                self,
                self.title,
                "Not enough valid data to compute a score.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        self.report_view.set_content(result.report)
