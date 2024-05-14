from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.timeseries.autocorrelation_widget import AutocorrelationWidget
from tse_analytics.views.analysis.timeseries.decomposition_widget import DecompositionWidget

# from tse_analytics.views.analysis.timeseries.prophet_forecasting_widget import ProphetForecastingWidget
from tse_analytics.views.analysis.timeseries.timeseries_widget_ui import Ui_TimeseriesWidget


class TimeseriesWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_TimeseriesWidget()
        self.ui.setupUi(self)

        self.decomposition_widget = DecompositionWidget()
        self.ui.tabWidget.addTab(self.decomposition_widget, "Decomposition")

        self.autocorrelation_widget = AutocorrelationWidget()
        self.ui.tabWidget.addTab(self.autocorrelation_widget, "Autocorrelation")

        # self.prophet_forecasting_widget = ProphetForecastingWidget()
        # self.ui.tabWidget.addTab(self.prophet_forecasting_widget, "Prophet Forecasting")

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.decomposition_widget.set_data(message.data)
        self.autocorrelation_widget.set_data(message.data)
        # self.prophet_forecasting_widget.set_data(message.data)

    def __clear(self):
        self.decomposition_widget.clear()
        self.autocorrelation_widget.clear()
        # self.prophet_forecasting_widget.clear()
