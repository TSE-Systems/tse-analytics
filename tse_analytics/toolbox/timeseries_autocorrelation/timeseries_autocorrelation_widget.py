from dataclasses import dataclass

import pandas as pd
from PySide6.QtCore import QSize, Qt, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_html_image_from_figure, get_h_spacer_widget
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.animal_selector import AnimalSelector
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

        self.canvas = MplCanvas(self)
        self._layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

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
        # Clear the plot
        self.canvas.clear(False)

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

        index = pd.DatetimeIndex(df["DateTime"])
        df.set_index(index, inplace=True)

        var_name = variable.name
        df[var_name] = df[var_name].interpolate(limit_direction="both")

        axs = self.canvas.figure.subplots(2, 1, sharex=True)
        self.canvas.figure.suptitle(f"Timeseries autocorrelation of {var_name} for animal {animal.id}")

        plot_acf(df[var_name], ax=axs[0], adjusted=False, title="Autocorrelation")
        axs[0].set_ylabel(var_name)
        plot_pacf(df[var_name], ax=axs[1], title="Partial Autocorrelation")
        axs[1].set_ylabel(var_name)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self):
        self.datatable.dataset.report += get_html_image_from_figure(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
