from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.histogram_widget_ui import Ui_HistogramWidget
from tse_analytics.views.misc.toast import Toast


class HistogramWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_HistogramWidget()
        self.ui.setupUi(self)

        self.help_path = "histogram.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count() - 1, plot_toolbar)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.toolButtonAnalyse.setDisabled(message.data is None)
        self.__clear()

    def __clear(self):
        self.ui.canvas.clear(True)

    def __get_plot_layout(self, number_of_elements: int):
        if number_of_elements == 1:
            return None
        elif number_of_elements <= 3:
            return number_of_elements, 1
        elif number_of_elements == 4:
            return 2, 2
        else:
            return round(number_of_elements / 3) + 1, 3

    def __analyze(self):
        if len(Manager.data.selected_variables) == 0:
            Toast(text="Please select variables first!", parent=self, duration=2000).show_toast()
            return

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        variables = [variable.name for variable in Manager.data.selected_variables]
        df = Manager.data.get_current_df(calculate_error=False, variables=variables)

        df.hist(
            column=variables,
            bins=self.ui.spinBoxBins.value(),
            log=self.ui.toolButtonLogScale.isChecked(),
            sharex=False,
            sharey=False,
            layout=self.__get_plot_layout(len(variables)),
            ax=ax,
        )

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
