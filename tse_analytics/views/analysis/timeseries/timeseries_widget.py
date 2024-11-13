import pandas as pd
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import MSTL, STL, seasonal_decompose

from tse_analytics.core import messaging
from tse_analytics.core.data.shared import Aggregation
from tse_analytics.core.helper import get_html_image, show_help
from tse_analytics.core.toaster import make_toast
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.analysis.timeseries.timeseries_widget_ui import Ui_TimeseriesWidget


class TimeseriesWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_TimeseriesWidget()
        self.ui.setupUi(self)

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)

        self.dataset: Dataset | None = None

        self.help_path = "timeseries.md"

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        self.ui.radioButtonAutocorrelation.toggled.connect(
            lambda toggled: self._set_options(False, False, False) if toggled else None
        )
        self.ui.radioButtonDecomposition.toggled.connect(
            lambda toggled: self._set_options(True, True, True) if toggled else None
        )

        self.ui.radioButtonMethodNaive.toggled.connect(
            lambda toggled: self._set_options(True, True, True) if toggled else None
        )
        self.ui.radioButtonMethodSTL.toggled.connect(
            lambda toggled: self._set_options(True, False, True) if toggled else None
        )
        self.ui.radioButtonMethodMSTL.toggled.connect(
            lambda toggled: self._set_options(True, False, True) if toggled else None
        )

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().addWidget(plot_toolbar)

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        if message.dataset is not None:
            self.dataset = message.dataset
            filtered_variables = {
                key: value
                for (key, value) in message.dataset.variables.items()
                if value.aggregation == Aggregation.MEAN
            }
            self.ui.animalSelector.set_data(message.dataset.animals)
            self.ui.variableSelector.set_data(filtered_variables)
        else:
            self.dataset = None
            self.ui.animalSelector.clear()
            self.ui.variableSelector.clear()
        self.ui.pushButtonUpdate.setDisabled(self.dataset is None)
        self.ui.pushButtonAddReport.setDisabled(self.dataset is None)
        self.ui.canvas.clear(True)

    def _set_options(
        self,
        show_method: bool,
        show_model: bool,
        show_period: bool,
    ):
        if show_method:
            self.ui.groupBoxMethod.show()
        else:
            self.ui.groupBoxMethod.hide()

        if show_model and self.ui.radioButtonMethodNaive.isChecked():
            self.ui.groupBoxModel.show()
        else:
            self.ui.groupBoxModel.hide()

        if show_period:
            self.ui.periodLabel.show()
            self.ui.periodSpinBox.show()
        else:
            self.ui.periodLabel.hide()
            self.ui.periodSpinBox.hide()

    def _update(self):
        if self.dataset.binning_settings.apply:
            make_toast(
                self,
                "Timeseries Analysis",
                "Timeseries analysis cannot be done when binning is active.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        if self.ui.radioButtonDecomposition.isChecked():
            self._update_decomposition()
        elif self.ui.radioButtonAutocorrelation.isChecked():
            self._update_autocorrelation()

    def _update_decomposition(self):
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

        period = self.ui.periodSpinBox.value()

        if self.ui.radioButtonMethodNaive.isChecked():
            model = "additive" if self.ui.radioButtonModelAdditive.isChecked() else "multiplicative"
            result = seasonal_decompose(
                df[var_name],
                period=period,
                model=model,
                extrapolate_trend="freq",
            )
        elif self.ui.radioButtonMethodSTL.isChecked():
            result = STL(
                endog=df[var_name],
                period=period,
            ).fit()
        elif self.ui.radioButtonMethodMSTL.isChecked():
            result = MSTL(
                endog=df[var_name],
                periods=period,
            ).fit()

        axs = self.ui.canvas.figure.subplots(4, 1, sharex=True)
        self.ui.canvas.figure.suptitle(f"Timeseries decomposition of {var_name} for animal {animal.id}")

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

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def _update_autocorrelation(self):
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
        html = get_html_image(self.ui.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, html))
