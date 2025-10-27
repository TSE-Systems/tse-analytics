from dataclasses import dataclass

import numpy as np
import pandas as pd
from PySide6.QtCore import QSize, Qt, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel
from astropy.timeseries import LombScargle
from matplotlib.backends.backend_qt import NavigationToolbar2QT

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_html_image_from_figure, get_h_spacer_widget
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class PeriodogramWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None


class PeriodogramWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: PeriodogramWidgetSettings = settings.value(self.__class__.__name__, PeriodogramWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Periodogram"

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
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(
            toolbar, self.datatable, check_binning=True, selected_mode=self._settings.group_by
        )
        toolbar.addWidget(self.group_by_selector)

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
            PeriodogramWidgetSettings(
                self.group_by_selector.currentText(),
                self.variableSelector.currentText(),
            ),
        )

    def _update(self):
        # Clear the plot
        self.canvas.clear(False)

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        variable = self.variableSelector.get_selected_variable()

        df = self.datatable.get_preprocessed_df(
            variables={variable.name: variable},
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=True,
        )

        t = df["DateTime"]
        y = df[variable.name]

        # Convert timestamps to numeric values (hours since start)
        reference_time = t.min()
        times_hours = [(ts - reference_time).total_seconds() / 3600 for ts in t]

        # Normalize activity for better analysis
        normalized_activity = (y - y.mean()) / y.std()

        # Define frequency grid (periods in hours)
        min_period = 1.0  # 1 hour
        max_period = 48.0  # 48 hours
        frequency = np.linspace(1 / max_period, 1 / min_period, 1000)

        # Calculate the periodogram
        power = LombScargle(times_hours, normalized_activity).power(frequency)

        # Convert frequency back to period in hours
        period = 1 / frequency

        # Get the most significant period
        strongest_period = period[np.argmax(power)]

        # Fold the data by the period
        phase = (np.array(times_hours) % strongest_period) / strongest_period
        phase_df = pd.DataFrame({"Phase": phase, variable.name: y})

        # Sort by phase for line plotting
        phase_df.sort_values("Phase", inplace=True)

        axs = self.canvas.figure.subplots(2, 1)

        axs[0].plot(period, power)
        axs[0].set(
            xlabel="Period (hours)",
            ylabel="Power",
            title=f"Lomb-Scargle Periodogram of {variable.name}. Strongest detected period: {strongest_period:.2f} hours",
        )

        # Add vertical lines at expected periods
        axs[0].axvline(x=24, color="r", linestyle="--", alpha=0.7, label="24h (Circadian)")
        axs[0].axvline(x=4, color="g", linestyle="--", alpha=0.7, label="4h (Ultradian)")
        axs[0].legend()

        axs[1].scatter(phase, y, alpha=0.5, marker=".")
        axs[1].plot(phase_df["Phase"], phase_df[variable.name], "r-", alpha=0.3)
        axs[1].set(
            xlabel=f"Phase (Period = {strongest_period:.2f} hours)",
            ylabel=variable.name,
            title="Phase-folded Data",
        )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self) -> None:
        self.datatable.dataset.report += get_html_image_from_figure(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
