import pandas as pd
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Aggregation
from tse_analytics.core.helper import get_html_image, get_h_spacer_widget
from tse_analytics.core.toaster import make_toast
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.animal_selector import AnimalSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class TimeseriesAutocorrelationWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Autocorrelation"

        self.dataset = dataset

        # Setup toolbar
        toolbar = QToolBar(
            "Data Plot Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction("Update").triggered.connect(self._update)
        toolbar.addSeparator()

        self.variableSelector = VariableSelector(toolbar)
        filtered_variables = {
            key: value for (key, value) in dataset.variables.items() if value.aggregation == Aggregation.MEAN
        }
        self.variableSelector.set_data(filtered_variables)
        toolbar.addWidget(self.variableSelector)

        self.animalSelector = AnimalSelector(toolbar)
        self.animalSelector.set_data(self.dataset.animals)
        toolbar.addWidget(self.animalSelector)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self.layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

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

        variable = self.variableSelector.get_selected_variable()
        animal = self.animalSelector.get_selected_animal()

        self.canvas.clear(False)

        df = self.dataset.get_timeseries_df(
            animal=animal,
            variable=variable,
        )

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
        self.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
