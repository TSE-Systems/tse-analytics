import pandas as pd
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.timeseries.autocorrelation_widget_ui import Ui_AutocorrelationWidget
from tse_analytics.views.misc.toast import Toast


class AutocorrelationWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
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
        if len(Manager.data.selected_variables) != 1:
            Toast(text="Please select a single variable.", parent=self, duration=2000).show_toast()
            return

        if len(Manager.data.selected_animals) != 1:
            Toast(text="Please select a single animal.", parent=self, duration=2000).show_toast()
            return

        self.ui.canvas.clear(False)

        variables = [variable.name for variable in Manager.data.selected_variables]
        var_name = Manager.data.selected_variables[0].name
        df = Manager.data.get_current_df(calculate_error=False, variables=variables, dropna=False)

        index = pd.DatetimeIndex(df["DateTime"])
        index = index.round("min")
        df.set_index(index, inplace=True)
        # df = df.asfreq("min")

        df[var_name] = df[var_name].interpolate(limit_direction="both")

        axs = self.ui.canvas.figure.subplots(2, 1, sharex=True)
        plot_acf(df[var_name], ax=axs[0], adjusted=self.ui.adjustedCheckBox.isChecked())
        plot_pacf(df[var_name], ax=axs[1])

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
