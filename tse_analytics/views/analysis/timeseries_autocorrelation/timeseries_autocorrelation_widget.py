import pandas as pd
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Aggregation
from tse_analytics.core.helper import get_html_image, show_help
from tse_analytics.core.toaster import make_toast
from tse_analytics.views.analysis.timeseries_autocorrelation.timeseries_autocorrelation_widget_ui import (
    Ui_TimeseriesAutocorrelationWidget,
)


class TimeseriesAutocorrelationWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_TimeseriesAutocorrelationWidget()
        self.ui.setupUi(self)

        self.title = "Autocorrelation"
        self.help_path = "Autocorrelation.md"

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().addWidget(plot_toolbar)

        self.dataset = dataset
        filtered_variables = {
            key: value for (key, value) in dataset.variables.items() if value.aggregation == Aggregation.MEAN
        }
        self.ui.animalSelector.set_data(dataset.animals)
        self.ui.variableSelector.set_data(filtered_variables)

    def _update(self):
        if self.dataset.binning_settings.apply:
            make_toast(
                self,
                self.title,
                "Timeseries analysis cannot be done when binning is active.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        variable = self.ui.variableSelector.get_selected_variable()

        animal = self.ui.animalSelector.get_selected_animal()

        self.ui.canvas.clear(False)

        df = self.dataset.get_timeseries_df(
            animal=animal,
            variable=variable,
        )

        index = pd.DatetimeIndex(df["DateTime"])
        df.set_index(index, inplace=True)

        var_name = variable.name
        df[var_name] = df[var_name].interpolate(limit_direction="both")

        axs = self.ui.canvas.figure.subplots(2, 1, sharex=True)
        self.ui.canvas.figure.suptitle(f"Timeseries autocorrelation of {var_name} for animal {animal.id}")

        plot_acf(df[var_name], ax=axs[0], adjusted=False, title="Autocorrelation")
        axs[0].set_ylabel(var_name)
        plot_pacf(df[var_name], ax=axs[1], title="Partial Autocorrelation")
        axs[1].set_ylabel(var_name)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def _add_report(self):
        self.dataset.report += get_html_image(self.ui.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
