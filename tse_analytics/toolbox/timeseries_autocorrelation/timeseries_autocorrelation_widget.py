from dataclasses import dataclass

from pyqttoast import ToastPreset
from PySide6.QtWidgets import QLabel, QToolBar, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget
from tse_analytics.toolbox.timeseries_autocorrelation.processor import get_timeseries_autocorrelation_result
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase
from tse_analytics.views.misc.animal_selector import AnimalSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class TimeseriesAutocorrelationWidgetSettings:
    selected_variable: str = None
    selected_animal: str = None


@toolbox_plugin(category="Time Series", label="Autocorrelation", icon=":/icons/timeseries.png", order=1)
class TimeseriesAutocorrelationWidget(ToolboxWidgetBase):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(
            datatable,
            TimeseriesAutocorrelationWidgetSettings,
            title="Autocorrelation",
            parent=parent,
        )

    def _create_toolbar_items(self, toolbar: QToolBar) -> None:
        self.variableSelector = VariableSelector(toolbar)
        filtered_variables = {
            key: value for (key, value) in self.datatable.variables.items() if value.aggregation == Aggregation.MEAN
        }
        self.variableSelector.set_data(filtered_variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addWidget(QLabel("Animal:"))
        self.animalSelector = AnimalSelector(toolbar)
        self.animalSelector.set_data(self.datatable.dataset, selected_animal=self._settings.selected_animal)
        toolbar.addWidget(self.animalSelector)

    def _get_settings_value(self):
        return TimeseriesAutocorrelationWidgetSettings(
            self.variableSelector.currentText(),
            self.animalSelector.currentText(),
        )

    def _update(self):
        self.report_view.clear()

        if self.datatable.dataset.binning_settings.apply:
            make_toast(
                self,
                self.title,
                "Timeseries analysis cannot be done when binning is active.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        variable = self.variableSelector.get_selected_variable()
        animal = self.animalSelector.get_selected_animal()

        columns = ["DateTime", "Timedelta", "Animal", variable.name]
        df = self.datatable.get_filtered_df(columns)
        df = df[df["Animal"] == animal.id]
        df.reset_index(drop=True, inplace=True)

        result = get_timeseries_autocorrelation_result(
            df,
            animal.id,
            variable.name,
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)
