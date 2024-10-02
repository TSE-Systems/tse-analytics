import pandas as pd
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import MSTL, STL, seasonal_decompose

from tse_analytics.core.helper import show_help, get_html_image, make_toast
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import AddToReportMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.timeseries.timeseries_widget_ui import Ui_TimeseriesWidget


class TimeseriesWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_TimeseriesWidget()
        self.ui.setupUi(self)

        self.help_path = "timeseries.md"

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().addWidget(plot_toolbar)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.pushButtonUpdate.setDisabled(message.data is None)
        self.ui.pushButtonAddReport.setDisabled(message.data is None)
        self._clear()
        if message.data is not None:
            self.ui.variableSelector.set_data(message.data.variables)

    def _clear(self):
        self.ui.variableSelector.clear()
        self.ui.canvas.clear(True)

    def _update(self):
        if self.ui.radioButtonDecomposition.isChecked():
            self._update_decomposition()
        elif self.ui.radioButtonAutocorrelation.isChecked():
            self._update_autocorrelation()

    def _update_decomposition(self):
        variable = self.ui.variableSelector.get_selected_variable()

        animal_ids = [animal.id for animal in Manager.data.selected_dataset.animals.values() if animal.enabled]
        if len(animal_ids) != 1:
            make_toast(
                self,
                "Timeseries Decomposition",
                "Please check a single animal in the Animals panel.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return
        animal_name = animal_ids[0]

        self.ui.canvas.clear(False)

        df = Manager.data.get_timeseries_df(
            variable=variable,
        )

        index = pd.DatetimeIndex(df["DateTime"])
        index = index.round("min")
        df.set_index(index, inplace=True)
        # df = df.asfreq("min")

        var_name = variable.name
        df[var_name] = df[var_name].interpolate(limit_direction="both")

        model = "additive" if self.ui.radioButtonModelAdditive.isChecked() else "multiplicative"
        period = self.ui.periodSpinBox.value()

        if self.ui.radioButtonMethodNaive.isChecked():
            result = seasonal_decompose(df[var_name], period=period, model=model, extrapolate_trend="freq")
        elif self.ui.radioButtonMethodSTL.isChecked():
            result = STL(
                endog=df[var_name],
                period=period,
            ).fit()
        elif self.ui.radioButtonMethodMSTL.isChecked():
            result = MSTL(
                endog=df[var_name],
                periods=(60, 60 * 24),
            ).fit()

        axs = self.ui.canvas.figure.subplots(4, 1, sharex=True)
        self.ui.canvas.figure.suptitle(f"Timeseries decomposition of {var_name} for animal {animal_name}")

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

        animal_ids = [animal.id for animal in Manager.data.selected_dataset.animals.values() if animal.enabled]
        if len(animal_ids) != 1:
            make_toast(
                self,
                "Timeseries Autocorrelation",
                "Please check a single animal in the Animals panel.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return
        animal_name = animal_ids[0]

        self.ui.canvas.clear(False)

        df = Manager.data.get_timeseries_df(
            variable=variable,
        )

        index = pd.DatetimeIndex(df["DateTime"])
        index = index.round("min")
        df.set_index(index, inplace=True)
        # df = df.asfreq("min")

        var_name = variable.name
        df[var_name] = df[var_name].interpolate(limit_direction="both")

        axs = self.ui.canvas.figure.subplots(2, 1, sharex=True)
        self.ui.canvas.figure.suptitle(f"Timeseries autocorrelation of {var_name} for animal {animal_name}")

        plot_acf(df[var_name], ax=axs[0], adjusted=False, title="Autocorrelation")
        axs[0].set_ylabel(var_name)
        plot_pacf(df[var_name], ax=axs[1], title="Partial Autocorrelation")
        axs[1].set_ylabel(var_name)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def _add_report(self):
        html = get_html_image(self.ui.canvas.figure)
        Manager.messenger.broadcast(AddToReportMessage(self, html))
