from dataclasses import dataclass

import pandas as pd
from PySide6.QtWidgets import QComboBox, QLabel, QSpinBox, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.toolbox.timeseries_decomposition.processor import get_timeseries_decomposition_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.animal_selector import AnimalSelector
from tse_analytics.views.misc.tooltip_widget import TooltipWidget
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class TimeseriesDecompositionWidgetSettings:
    selected_variable: str = None
    selected_animal: str = None
    period: int = 48
    method: str = "Naive"
    model: str = "Additive"


@toolbox_plugin(category="Time Series", label="Decomposition", icon=":/icons/timeseries.png", order=0)
class TimeseriesDecompositionWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            TimeseriesDecompositionWidgetSettings,
            title="Decomposition",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addWidget(QLabel("Animal:"))
        self.animalSelector = AnimalSelector(toolbar)
        self.animalSelector.set_data(self.datatable.dataset, selected_animal=self._settings.selected_animal)
        toolbar.addWidget(self.animalSelector)

        toolbar.addWidget(QLabel("Period:"))
        self.period_spin_box = QSpinBox(
            toolbar,
            minimum=1,
            maximum=10000,
            singleStep=1,
            value=int(pd.Timedelta("24:00:00") / self.datatable.sampling_interval)
            if self.datatable.sampling_interval is not None
            else self._settings.period,
        )
        toolbar.addWidget(self.period_spin_box)

        toolbar.addWidget(QLabel("Method:"))
        self.method_combo_box = QComboBox(toolbar)
        self.method_combo_box.addItems(["Naive", "STL (smoothing)"])
        self.method_combo_box.setCurrentText(self._settings.method)
        self.method_combo_box.currentTextChanged.connect(lambda text: self.model_combo_box.setEnabled(text == "Naive"))
        toolbar.addWidget(self.method_combo_box)

        toolbar.addWidget(QLabel("Model:"))
        self.model_combo_box = QComboBox(toolbar)
        self.model_combo_box.addItems(["Additive", "Multiplicative"])
        self.model_combo_box.setCurrentText(self._settings.model)
        toolbar.addWidget(self.model_combo_box)

        toolbar.addWidget(TooltipWidget("<b>Period:</b> number of observations per cycle"))

    def _get_settings_value(self):
        return TimeseriesDecompositionWidgetSettings(
            self.variableSelector.currentText(),
            self.animalSelector.currentText(),
            self.period_spin_box.value(),
            self.method_combo_box.currentText(),
            self.model_combo_box.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        variable = self.variableSelector.get_selected_variable()
        animal = self.animalSelector.get_selected_animal()

        columns = ["Timedelta", "Animal", variable.name]
        df = self.datatable.get_filtered_df(columns)
        df = df[df["Animal"] == animal.id]
        df.reset_index(drop=True, inplace=True)

        result = get_timeseries_decomposition_result(
            df,
            animal.id,
            variable.name,
            self.period_spin_box.value(),
            self.method_combo_box.currentText(),
            self.model_combo_box.currentText(),
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
