import seaborn as sns
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import GroupingMode
from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.distribution_widget_ui import Ui_DistributionWidget
from tse_analytics.views.misc.toast import Toast


class DistributionWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_DistributionWidget()
        self.ui.setupUi(self)

        self.help_path = "distribution.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.variable = ""
        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)

        self.color_factor = None
        self.ui.factorSelector.currentTextChanged.connect(self.__factor_changed)

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count() - 1, plot_toolbar)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.toolButtonAnalyse.setDisabled(message.data is None)
        self.__clear()
        if message.data is not None:
            self.ui.variableSelector.set_data(message.data.variables)
            self.ui.factorSelector.set_data(message.data.factors)

    def __clear(self):
        self.ui.variableSelector.clear()
        self.ui.factorSelector.clear()
        self.ui.canvas.clear()

    def __variable_changed(self, variable: str):
        self.variable = variable

    def __factor_changed(self, factor: str):
        if factor == "":
            self.color_factor = None
        else:
            self.color_factor = factor

    def __analyze(self):
        if Manager.data.grouping_mode == GroupingMode.FACTORS and Manager.data.selected_factor is None:
            Toast(text="Please select a factor first!", parent=self, duration=2000).show_toast()
            return

        df = Manager.data.get_current_df(variables=[self.variable])

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        match Manager.data.grouping_mode:
            case GroupingMode.FACTORS:
                x = Manager.data.selected_factor.name
            case GroupingMode.RUNS:
                x = "Run"
            case _:
                x = "Animal"

        df[x] = df[x].cat.remove_unused_categories()

        if self.color_factor is None:
            sns.violinplot(data=df, x=x, y=self.variable, ax=ax)
        else:
            sns.boxplot(data=df, x=x, y=self.variable, hue=self.color_factor, gap=0.1, ax=ax)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
