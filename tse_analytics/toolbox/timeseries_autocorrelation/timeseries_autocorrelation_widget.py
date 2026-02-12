from dataclasses import dataclass

from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QInputDialog, QLabel, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import Aggregation
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget, get_h_spacer_widget
from tse_analytics.toolbox.timeseries_autocorrelation.processor import get_timeseries_autocorrelation_result
from tse_analytics.views.misc.animal_selector import AnimalSelector
from tse_analytics.views.misc.report_edit import ReportEdit
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class TimeseriesAutocorrelationWidgetSettings:
    selected_variable: str = None
    selected_animal: str = None


class TimeseriesAutocorrelationWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: TimeseriesAutocorrelationWidgetSettings = settings.value(
            self.__class__.__name__, TimeseriesAutocorrelationWidgetSettings()
        )

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Autocorrelation"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        self.variableSelector = VariableSelector(toolbar)
        filtered_variables = {
            key: value for (key, value) in datatable.variables.items() if value.aggregation == Aggregation.MEAN
        }
        self.variableSelector.set_data(filtered_variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addWidget(QLabel("Animal:"))
        self.animalSelector = AnimalSelector(toolbar)
        self.animalSelector.set_data(self.datatable.dataset, selected_animal=self._settings.selected_animal)
        toolbar.addWidget(self.animalSelector)

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
            TimeseriesAutocorrelationWidgetSettings(
                self.variableSelector.currentText(),
                self.animalSelector.currentText(),
            ),
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
