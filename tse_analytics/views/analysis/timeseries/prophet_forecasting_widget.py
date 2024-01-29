import pandas as pd
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.timeseries.prophet_forecasting_widget_ui import Ui_ProphetForecastingWidget
from tse_analytics.views.misc.toast import Toast


class ProphetForecastingWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ProphetForecastingWidget()
        self.ui.setupUi(self)

        self.help_path = "timeseries-prophet.md"
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
        df = Manager.data.get_current_df(calculate_error=False, variables=variables)

        df = pd.concat({"ds": df["DateTime"], "y": df[Manager.data.selected_variables[0].name]}, axis=1)

        m = Prophet(changepoint_prior_scale=self.ui.changepointPriorScaleDoubleSpinBox.value())
        m.fit(df=df)

        if self.ui.radioButtonDayFrequency.isChecked():
            freq = "D"
        elif self.ui.radioButtonHourFrequency.isChecked():
            freq = "H"
        elif self.ui.radioButtonMinuteFrequency.isChecked():
            freq = "min"
        elif self.ui.radioButtonSecondFrequency.isChecked():
            freq = "S"

        future = m.make_future_dataframe(
            periods=self.ui.periodsSpinBox.value(), freq=freq, include_history=self.ui.showHistoryCheckBox.isChecked()
        )

        forecast = m.predict(future)

        ax = self.ui.canvas.figure.add_subplot(111)
        fig = m.plot(forecast, ax=ax)

        if self.ui.showTrendCheckBox.isChecked():
            add_changepoints_to_plot(fig.gca(), m, forecast)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
