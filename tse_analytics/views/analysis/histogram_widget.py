from typing import Optional

from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage, ClearDataMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.histogram_widget_ui import Ui_HistogramWidget


class HistogramWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_HistogramWidget()
        self.ui.setupUi(self)

        self.help_path = "docs/histogram.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count()-2, NavigationToolbar2QT(self.ui.canvas, self))

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.__clear()

    def __on_clear_data(self, message: ClearDataMessage):
        self.__clear()

    def __clear(self):
        self.ui.canvas.clear()

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
        if Manager.data.selected_dataset is None or len(Manager.data.selected_variables) == 0:
            return

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        df = Manager.data.selected_dataset.active_df
        selected_variables = Manager.data.selected_variables
        columns = [item.name for item in selected_variables]

        df.hist(
            column=columns,
            bins=50,
            sharex=False,
            sharey=False,
            layout=self.__get_plot_layout(len(selected_variables)),
            ax=ax,
        )

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
