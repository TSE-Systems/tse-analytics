from typing import Optional

import pandas as pd
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from statsmodels.tsa.seasonal import seasonal_decompose

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.timeseries.decomposition_widget_ui import Ui_DecompositionWidget
from tse_analytics.views.misc.toast import Toast


class DecompositionWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.ui = Ui_DecompositionWidget()
        self.ui.setupUi(self)

        self.help_path = "timeseries-decomposition.md"
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
        df.set_index(pd.DatetimeIndex(df["DateTime"]), inplace=True)

        x = df[Manager.data.selected_variables[0].name]
        result = seasonal_decompose(x, period=60*24)
        # result.plot()

        ax = self.ui.canvas.figure.add_subplot(221)
        ax.plot(result.observed, label="Original time series", color="blue")
        ax.legend()

        ax = self.ui.canvas.figure.add_subplot(222)
        ax.plot(result.trend, label="Trend of time series", color="blue")
        ax.legend()

        ax = self.ui.canvas.figure.add_subplot(223)
        ax.plot(result.seasonal, label="Seasonality of time series", color="blue")
        ax.legend()

        ax = self.ui.canvas.figure.add_subplot(224)
        ax.plot(result.resid, label="Decomposition residuals of time series", color="blue")
        ax.legend()

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
