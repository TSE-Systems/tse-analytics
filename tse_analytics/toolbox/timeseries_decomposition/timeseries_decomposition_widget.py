from dataclasses import dataclass

import pandas as pd
from PySide6.QtCore import QSize, Qt, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QSpinBox, QComboBox
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from statsmodels.tsa.seasonal import STL, seasonal_decompose

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.views.misc.MplCanvas import MplCanvas
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


class TimeseriesDecompositionWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: TimeseriesDecompositionWidgetSettings = settings.value(
            self.__class__.__name__, TimeseriesDecompositionWidgetSettings()
        )

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Decomposition"

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
        # variables = {
        #     key: value for (key, value) in datatable.variables.items() if value.aggregation == Aggregation.MEAN
        # }
        self.variableSelector.set_data(datatable.variables, selected_variable=self._settings.selected_variable)
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

        self._layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self._layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

        toolbar.addWidget(TooltipWidget("<b>Period:</b> number of observations per cycle"))

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            TimeseriesDecompositionWidgetSettings(
                self.variableSelector.currentText(),
                self.animalSelector.currentText(),
                self.period_spin_box.value(),
                self.method_combo_box.currentText(),
                self.model_combo_box.currentText(),
            ),
        )

    def _update(self):
        # Clear the plot
        self.canvas.clear(False)

        variable = self.variableSelector.get_selected_variable()
        animal = self.animalSelector.get_selected_animal()

        columns = ["Timedelta", "Animal", variable.name]
        df = self.datatable.get_filtered_df(columns)
        df = df[df["Animal"] == animal.id]
        df.reset_index(drop=True, inplace=True)

        index = pd.TimedeltaIndex(df["Timedelta"])
        df.set_index(index, inplace=True)

        var_name = variable.name
        # TODO: not sure interpolation should be used...
        df[var_name] = df[var_name].interpolate(limit_direction="both")
        period = self.period_spin_box.value()

        match self.method_combo_box.currentText():
            case "STL (smoothing)":
                result = STL(
                    endog=df[var_name],
                    period=period,
                ).fit()
            case _:
                model = self.model_combo_box.currentText().lower()
                result = seasonal_decompose(
                    df[var_name],
                    period=period,
                    model=model,
                    extrapolate_trend="freq",
                )

        # df = pd.concat({
        #     "Observed": result.observed,
        #     "Trend": result.trend,
        #     "Seasonal": result.seasonal,
        #     "Residual": result.resid,
        # }, axis=1).reset_index()
        #
        # (
        #     so.Plot(
        #         df,
        #         x="Timedelta",
        #     )
        #     .pair(y=("Observed", "Trend", "Seasonal", "Residual"))
        #     .add(so.Line(), so.Est())  # Line with mean estimate
        #     .on(self.canvas.figure)
        #     .plot(True)
        # )

        axs = self.canvas.figure.subplots(4, 1, sharex=True)
        self.canvas.figure.suptitle(f"Variable: {var_name}. Animal: {animal.id}. Period: {period}")

        result.observed.plot(ax=axs[0], ylabel="Observed", lw=1)
        result.trend.plot(ax=axs[1], ylabel="Trend", lw=1)
        result.seasonal.plot(ax=axs[2], ylabel="Seasonal", lw=1)
        result.resid.plot(ax=axs[3], ylabel="Residual", lw=1, marker=".", markersize=2, linestyle="none")

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self):
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
