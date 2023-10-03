from typing import Optional

import pingouin as pg
from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from numpy import isnan

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage, ClearDataMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.normality_widget_ui import Ui_NormalityWidget
from tse_datatools.analysis.grouping_mode import GroupingMode


class NormalityWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_NormalityWidget()
        self.ui.setupUi(self)

        self.help_path = "docs/normality.md"
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

        df = Manager.data.get_current_df(calculate_error=False, variables=[self.variable])

        self.ui.canvas.clear(False)

        if Manager.data.grouping_mode == GroupingMode.FACTORS:
            if len(Manager.data.selected_factor.groups) == 0:
                self.ui.canvas.figure.suptitle("Please assign animals to groups first")
                self.ui.canvas.draw()
                return

            factor_name = Manager.data.selected_factor.name
            groups = df[factor_name].unique()
            nrows, ncols = self.__get_cells(len(groups))
            for index, group in enumerate(groups):
                # TODO: NaN check
                if group != group:
                    continue
                ax = self.ui.canvas.figure.add_subplot(nrows, ncols, index + 1)
                # stats.probplot(df[df[factor_name] == group][variable], dist="norm", plot=ax)
                pg.qqplot(df[df[factor_name] == group][self.variable], dist="norm", ax=ax)
                ax.set_title(group)
        else:
            animals = (
                Manager.data.selected_animals
                if len(Manager.data.selected_animals) > 0
                else Manager.data.selected_dataset.animals.values()
            )
            nrows, ncols = self.__get_cells(len(animals))
            for index, animal in enumerate(animals):
                ax = self.ui.canvas.figure.add_subplot(nrows, ncols, index + 1)
                # stats.probplot(df[df["Animal"] == group][variable], dist="norm", plot=ax)
                pg.qqplot(df[df["Animal"] == animal.id][self.variable], dist="norm", ax=ax)
                ax.set_title(animal.id)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def __get_cells(self, number_of_elements: int):
        if number_of_elements == 1:
            return 1, 1
        elif number_of_elements == 2:
            return 1, 2
        elif number_of_elements <= 4:
            return 2, 2
        else:
            return round(number_of_elements / 3) + 1, 3
