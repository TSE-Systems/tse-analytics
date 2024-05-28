import seaborn as sns
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DataChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.tools.compare_runs_widget_ui import Ui_CompareRunsWidget


class CompareRunsWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_CompareRunsWidget()
        self.ui.setupUi(self)

        self.variable = ""
        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count() - 1, plot_toolbar)

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
        df = Manager.data.get_current_df(variables=[self.variable])

        runs = df["Run"].unique()
        df["Run"] = df["Run"].astype(int)
        df["Bin"] = df["Bin"].astype(int)

        for _i, run in enumerate(runs):
            run_df = df[df["Run"] == run]
            first_bin = run_df["Bin"].values[0]
            old_bins = df[df["Run"] == run]["Bin"].astype(int)
            new_bins = old_bins - first_bin
            df.loc[df["Run"] == run, "Bin"] = new_bins

        df["Run"] = df["Run"].astype("category")
        df["Bin"] = df["Bin"].astype("category")

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        sns.lineplot(data=df, x="Bin", y=self.variable, hue="Run", errorbar=None, ax=ax)

        # dark_cycle_start = Manager.data.selected_dataset.binning_settings.time_cycles_settings.dark_cycle_start
        # light_cycle_start = Manager.data.selected_dataset.binning_settings.time_cycles_settings.light_cycle_start
        #
        # unit = "H"
        # match Manager.data.selected_dataset.binning_settings.time_intervals_settings.unit:
        #     case "day":
        #         unit = "D"
        #     case "hour":
        #         unit = "H"
        #     case "minute":
        #         unit = "min"
        # delta = pd.Timedelta(f"{Manager.data.selected_dataset.binning_settings.time_intervals_settings.delta}{unit}")
        #
        # start_timestamp = Manager.data.selected_dataset.start_timestamp
        #
        # z = 1 / delta
        #
        # x1 = dark_cycle_start * z
        # x2 = light_cycle_start * z
        # ax.axvspan(3, 5, alpha=0.1)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
