import base64
from io import BytesIO

import pandas as pd
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import MSTL, STL, seasonal_decompose

from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import AddToReportMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.timeseries.timeseries_widget_ui import Ui_TimeseriesWidget
from tse_analytics.views.misc.notification import Notification


class TimeseriesWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_TimeseriesWidget()
        self.ui.setupUi(self)

        self.help_path = "timeseries.md"

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self.__update)
        self.ui.pushButtonAddReport.clicked.connect(self.__add_report)

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().insertWidget(0, plot_toolbar)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.pushButtonUpdate.setDisabled(message.data is None)
        self.ui.pushButtonAddReport.setDisabled(message.data is None)
        self.__clear()
        if message.data is not None:
            self.ui.variableSelector.set_data(message.data.variables)

    def __clear(self):
        self.ui.variableSelector.clear()
        self.ui.canvas.clear(True)

    def __update(self):
        if self.ui.radioButtonDecomposition.isChecked():
            self.__update_decomposition()
        elif self.ui.radioButtonAutocorrelation.isChecked():
            self.__update_autocorrelation()

    def __update_decomposition(self):
        variable = self.ui.variableSelector.currentText()
        if variable == "":
            Notification(text="Please select a variable.", parent=self, duration=2000).show_notification()
            return

        if len(Manager.data.selected_animals) != 1:
            Notification(
                text="Please select an animal in Animals panel.", parent=self, duration=2000
            ).show_notification()
            return

        animal_name = Manager.data.selected_animals[0].id

        self.ui.canvas.clear(False)

        df = Manager.data.get_data_view_df(
            variables=[variable],
            split_mode=SplitMode.ANIMAL,
            selected_factor=None,
            dropna=False,
        )

        index = pd.DatetimeIndex(df["DateTime"])
        index = index.round("min")
        df.set_index(index, inplace=True)
        # df = df.asfreq("min")

        df[variable] = df[variable].interpolate(limit_direction="both")

        model = "additive" if self.ui.radioButtonModelAdditive.isChecked() else "multiplicative"
        period = self.ui.periodSpinBox.value()

        if self.ui.radioButtonMethodNaive.isChecked():
            result = seasonal_decompose(df[variable], period=period, model=model, extrapolate_trend="freq")
        elif self.ui.radioButtonMethodSTL.isChecked():
            result = STL(
                endog=df[variable],
                period=period,
            ).fit()
        elif self.ui.radioButtonMethodMSTL.isChecked():
            result = MSTL(
                endog=df[variable],
                periods=(60, 60 * 24),
            ).fit()

        axs = self.ui.canvas.figure.subplots(4, 1, sharex=True)
        self.ui.canvas.figure.suptitle(f"Timeseries decomposition of {variable} for animal {animal_name}")

        axs[0].plot(result.observed, label="Observed", lw=1)
        axs[0].set_ylabel(variable)
        axs[0].legend(loc="upper right")

        axs[1].plot(result.trend, label="Trend Component", lw=1)
        axs[1].set_ylabel(variable)
        axs[1].legend(loc="upper right")

        axs[2].plot(result.seasonal, label="Seasonal Component", lw=1)
        axs[2].set_ylabel(variable)
        axs[2].legend(loc="upper right")

        axs[3].plot(result.resid, label="Residual Component", marker=".", markersize=2, linestyle="none")
        axs[3].set_ylabel(variable)
        nobs = result.observed.shape[0]
        xlim = result.observed.index[0], result.observed.index[nobs - 1]
        axs[3].plot(xlim, (0, 0), color="#000000", zorder=-3)
        axs[3].legend(loc="upper right")

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def __update_autocorrelation(self):
        variable = self.ui.variableSelector.currentText()
        if variable == "":
            Notification(text="Please select a variable.", parent=self, duration=2000).show_notification()
            return

        if len(Manager.data.selected_animals) != 1:
            Notification(
                text="Please select an animal in Animals panel.", parent=self, duration=2000
            ).show_notification()
            return

        animal_name = Manager.data.selected_animals[0].id

        self.ui.canvas.clear(False)

        df = Manager.data.get_data_view_df(
            variables=[variable],
            split_mode=SplitMode.ANIMAL,
            selected_factor=None,
            dropna=False,
        )

        index = pd.DatetimeIndex(df["DateTime"])
        index = index.round("min")
        df.set_index(index, inplace=True)
        # df = df.asfreq("min")

        df[variable] = df[variable].interpolate(limit_direction="both")

        axs = self.ui.canvas.figure.subplots(2, 1, sharex=True)
        self.ui.canvas.figure.suptitle(f"Timeseries autocorrelation of {variable} for animal {animal_name}")

        plot_acf(df[variable], ax=axs[0], adjusted=False, title="Autocorrelation")
        axs[0].set_ylabel(variable)
        plot_pacf(df[variable], ax=axs[1], title="Partial Autocorrelation")
        axs[1].set_ylabel(variable)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def __add_report(self):
        io = BytesIO()
        self.ui.canvas.figure.savefig(io, format="png")
        encoded = base64.b64encode(io.getvalue()).decode("utf-8")
        html = f"<img src='data:image/png;base64,{encoded}'>"
        Manager.messenger.broadcast(AddToReportMessage(self, html))
