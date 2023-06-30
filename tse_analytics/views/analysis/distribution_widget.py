from typing import Optional

import seaborn as sns
from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage, ClearDataMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.distribution_widget_ui import Ui_DistributionWidget
from tse_datatools.analysis.grouping_mode import GroupingMode


class DistributionWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_DistributionWidget()
        self.ui.setupUi(self)

        self.help_path = "docs/distribution.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.variable = ""
        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)

        self.ui.horizontalLayout.insertWidget(
            self.ui.horizontalLayout.count() - 2, NavigationToolbar2QT(self.ui.canvas, self)
        )

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.__clear()
        self.ui.variableSelector.set_data(message.data.variables)

    def __on_clear_data(self, message: ClearDataMessage):
        self.__clear()

    def __clear(self):
        self.ui.variableSelector.clear()
        self.ui.canvas.clear()

    def __variable_changed(self, variable: str):
        self.variable = variable

    def __analyze(self):
        if Manager.data.selected_dataset is None or (
            Manager.data.grouping_mode == GroupingMode.FACTORS and Manager.data.selected_factor is None
        ):
            return

        df = Manager.data.selected_dataset.active_df

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        # sns.boxplot(data=df, x="Group", y=self.variable, ax=self.ax, color="green")
        x = Manager.data.selected_factor.name if Manager.data.grouping_mode == GroupingMode.FACTORS else "Animal"
        sns.violinplot(data=df, x=x, y=self.variable, ax=ax)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
