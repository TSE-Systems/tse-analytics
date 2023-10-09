from typing import Optional

from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qt import NavigationToolbar2QT
import seaborn as sns

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DataChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.tools.compare_runs_widget_ui import Ui_CompareRunsWidget


class CompareRunsWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_CompareRunsWidget()
        self.ui.setupUi(self)

        self.variable = ""
        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)

        self.ui.horizontalLayout.insertWidget(
            self.ui.horizontalLayout.count() - 1, NavigationToolbar2QT(self.ui.canvas, self)
        )

        self.ui.variableSelector.set_data(Manager.data.selected_dataset.variables)
        self.__prepare_data()

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DataChangedMessage, self.__on_data_changed)

    def __on_data_changed(self, message: DataChangedMessage):
        pass

    def __variable_changed(self, variable: str):
        self.variable = variable
        self.__prepare_data()

    def __prepare_data(self):
        df = Manager.data.get_current_df(calculate_error=False, variables=[self.variable])

        runs = df["Run"].unique()
        for i, run in enumerate(runs):
            run_df = df[df["Run"] == run]
            first_bin = run_df["Bin"].values[0]
            old_bins = df[df["Run"] == run]["Bin"].astype(int)
            new_bins = old_bins - first_bin
            df.loc[df["Run"] == run, "Bin"] = new_bins

        df["Bin"] = df["Bin"].astype("category")

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        sns.lineplot(data=df, x="Bin", y=self.variable, hue="Run", errorbar=None, ax=ax)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
