import pandas as pd
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from statsmodels.tsa.seasonal import MSTL, STL, seasonal_decompose

from tse_analytics.core.data.shared import GroupingMode
from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.timeseries.decomposition_widget_ui import Ui_DecompositionWidget
from tse_analytics.views.misc.toast import Toast


class DecompositionWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
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
        if len(Manager.data.selected_variables) != 1:
            Toast(text="Please select a single variable.", parent=self, duration=2000).show_toast()
            return

        if len(Manager.data.selected_animals) != 1:
            Toast(text="Please select a single animal.", parent=self, duration=2000).show_toast()
            return

        self.ui.canvas.clear(False)

        variables = [variable.name for variable in Manager.data.selected_variables]
        var_name = Manager.data.selected_variables[0].name

        df = Manager.data.get_current_df(
            variables=variables,
            grouping_mode=GroupingMode.ANIMALS,
            selected_factor=None,
            dropna=False,
        )

        index = pd.DatetimeIndex(df["DateTime"])
        index = index.round("min")
        df.set_index(index, inplace=True)
        # df = df.asfreq("min")

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

        axs[0].plot(result.observed, label="Observed", lw=1)
        axs[0].legend()

        axs[1].plot(result.trend, label="Trend Component", lw=1)
        axs[1].legend()

        axs[2].plot(result.seasonal, label="Seasonal Component", lw=1)
        axs[2].legend()

        axs[3].plot(result.resid, label="Residual Component", marker=".", markersize=2, linestyle="none")
        nobs = result.observed.shape[0]
        xlim = result.observed.index[0], result.observed.index[nobs - 1]
        axs[3].plot(xlim, (0, 0), color="#000000", zorder=-3)
        axs[3].legend()

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
