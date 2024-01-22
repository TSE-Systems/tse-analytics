from typing import Optional

import pandas as pd
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from darts import TimeSeries
from darts.utils.missing_values import fill_missing_values
from darts.utils.statistics import plot_residuals_analysis, plot_acf, plot_pacf
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.timeseries.autocorrelation_widget_ui import Ui_AutocorrelationWidget
from tse_analytics.views.misc.toast import Toast


class AutocorrelationWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.ui = Ui_AutocorrelationWidget()
        self.ui.setupUi(self)

        self.help_path = "timeseries-autocorrelation.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count() - 1, plot_toolbar)

    def set_data(self, data):
        self.ui.toolButtonAnalyse.setDisabled(data is None)
        self.clear()

    def clear(self):
        self.ui.canvas.clear(True)

    def __analyze(self):
        if len(Manager.data.selected_variables) == 0:
            Toast(text="Please select variables first!", duration=2000, parent=self).show_toast()
            return

        self.ui.canvas.clear(False)

        variables = [variable.name for variable in Manager.data.selected_variables]
        df = Manager.data.get_current_df(calculate_error=False, variables=variables, dropna=True)

        index = pd.DatetimeIndex(df["DateTime"])
        index = index.round("min")
        df.set_index(index, inplace=True)
        # df = df.asfreq("min")

        timeseries = TimeSeries.from_dataframe(df=df, value_cols=Manager.data.selected_variables[0].name, freq="min")

        timeseries = fill_missing_values(timeseries, fill="auto")

        axs = self.ui.canvas.figure.subplots(2, 1, sharex=True)
        plot_acf(timeseries, alpha=0.05, axis=axs[0], default_formatting=True)
        plot_pacf(timeseries, alpha=0.05, axis=axs[1], default_formatting=True)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
