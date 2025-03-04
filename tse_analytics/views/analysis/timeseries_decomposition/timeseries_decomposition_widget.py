import pandas as pd
from PySide6.QtGui import QIcon
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar
from statsmodels.tsa.seasonal import MSTL, STL, seasonal_decompose

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Aggregation
from tse_analytics.core.helper import get_html_image, get_h_spacer_widget, get_widget_tool_button
from tse_analytics.core.toaster import make_toast
from tse_analytics.views.analysis.timeseries_decomposition.timeseries_decomposition_settings_widget_ui import \
    Ui_TimeseriesDecompositionSettingsWidget
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.animal_selector import AnimalSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class TimeseriesDecompositionWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Decomposition"

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

        self.settings_widget = QWidget()
        self.settings_widget_ui = Ui_TimeseriesDecompositionSettingsWidget()
        self.settings_widget_ui.setupUi(self.settings_widget)
        settings_button = get_widget_tool_button(
            toolbar,
            self.settings_widget,
            "Settings",
            QIcon(":/icons/icons8-settings-16.png"),
        )
        toolbar.addWidget(settings_button)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self.layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

        self.settings_widget_ui.radioButtonMethodNaive.toggled.connect(lambda toggled: self._set_options(True) if toggled else None)
        self.settings_widget_ui.radioButtonMethodSTL.toggled.connect(lambda toggled: self._set_options(False) if toggled else None)
        self.settings_widget_ui.radioButtonMethodMSTL.toggled.connect(lambda toggled: self._set_options(False) if toggled else None)

    def _set_options(
        self,
        show_model: bool,
    ):
        if show_model and self.settings_widget_ui.radioButtonMethodNaive.isChecked():
            self.settings_widget_ui.groupBoxModel.show()
        else:
            self.settings_widget_ui.groupBoxModel.hide()

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

        period = self.settings_widget_ui.periodSpinBox.value()

        if self.settings_widget_ui.radioButtonMethodNaive.isChecked():
            model = "additive" if self.settings_widget_ui.radioButtonModelAdditive.isChecked() else "multiplicative"
            result = seasonal_decompose(
                df[var_name],
                period=period,
                model=model,
                extrapolate_trend="freq",
            )
        elif self.settings_widget_ui.radioButtonMethodSTL.isChecked():
            result = STL(
                endog=df[var_name],
                period=period,
            ).fit()
        elif self.settings_widget_ui.radioButtonMethodMSTL.isChecked():
            result = MSTL(
                endog=df[var_name],
                periods=period,
            ).fit()

        axs = self.canvas.figure.subplots(4, 1, sharex=True)
        self.canvas.figure.suptitle(f"Timeseries decomposition of {var_name} for animal {animal.id}")

        axs[0].plot(result.observed, label="Observed", lw=1)
        axs[0].set_ylabel(var_name)
        axs[0].legend(loc="upper right")

        axs[1].plot(result.trend, label="Trend Component", lw=1)
        axs[1].set_ylabel(var_name)
        axs[1].legend(loc="upper right")

        axs[2].plot(result.seasonal, label="Seasonal Component", lw=1)
        axs[2].set_ylabel(var_name)
        axs[2].legend(loc="upper right")

        axs[3].plot(result.resid, label="Residual Component", marker=".", markersize=2, linestyle="none")
        axs[3].set_ylabel(var_name)
        nobs = result.observed.shape[0]
        xlim = result.observed.index[0], result.observed.index[nobs - 1]
        axs[3].plot(xlim, (0, 0), color="#000000", zorder=-3)
        axs[3].legend(loc="upper right")

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self):
        self.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
