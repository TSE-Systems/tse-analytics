import pingouin as pg
import seaborn as sns
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QDir, QSize, QTemporaryFile
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import AddToReportMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.exploration_widget_ui import Ui_ExplorationWidget
from tse_analytics.views.misc.notification import Notification


class ExplorationWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_ExplorationWidget()
        self.ui.setupUi(self)

        self.help_path = "exploration.md"

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self.__update)
        self.ui.pushButtonAddReport.clicked.connect(self.__add_report)

        self.ui.radioButtonHistogram.toggled.connect(lambda: self.ui.groupBoxDistribution.setEnabled(False))
        self.ui.radioButtonDistribution.toggled.connect(lambda: self.ui.groupBoxDistribution.setEnabled(True))
        self.ui.radioButtonNormality.toggled.connect(lambda: self.ui.groupBoxDistribution.setEnabled(False))

        self.ui.radioButtonSplitTotal.toggled.connect(lambda: self.ui.factorSelector.setEnabled(False))
        self.ui.radioButtonSplitByAnimal.toggled.connect(lambda: self.ui.factorSelector.setEnabled(False))
        self.ui.radioButtonSplitByFactor.toggled.connect(lambda: self.ui.factorSelector.setEnabled(True))
        self.ui.radioButtonSplitByRun.toggled.connect(lambda: self.ui.factorSelector.setEnabled(False))

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().insertWidget(0, plot_toolbar)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.pushButtonUpdate.setDisabled(message.data is None)
        self.ui.pushButtonAddReport.setDisabled(message.data is None)
        self.__clear()
        if message.data is not None:
            self.ui.variableSelector.set_data(message.data.variables)
            self.ui.factorSelector.set_data(message.data.factors, add_empty_item=False)

    def __clear(self):
        self.ui.variableSelector.clear()
        self.ui.factorSelector.clear()
        self.ui.canvas.clear(True)

    def __update(self):
        if self.ui.radioButtonSplitByFactor.isChecked() and self.ui.factorSelector.currentText() == "":
            Notification(text="Please select factor.", parent=self, duration=2000).show_notification()
            return

        if self.ui.radioButtonHistogram.isChecked():
            self.__update_histogram_plot()
        elif self.ui.radioButtonDistribution.isChecked():
            self.__update_distribution_plot()
        elif self.ui.radioButtonNormality.isChecked():
            self.__update_normality_plot()

    def __update_histogram_plot(self):
        variable = self.ui.variableSelector.currentText()
        selected_factor = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        by = None
        if self.ui.radioButtonSplitByAnimal.isChecked():
            split_mode = SplitMode.ANIMAL
            by = "Animal"
        elif self.ui.radioButtonSplitByRun.isChecked():
            split_mode = SplitMode.RUN
            by = "Run"
        elif self.ui.radioButtonSplitByFactor.isChecked():
            split_mode = SplitMode.FACTOR
            by = selected_factor

        df = Manager.data.get_current_df(
            variables=[variable],
            split_mode=split_mode,
            selected_factor=selected_factor,
            dropna=False,
        )

        number_of_elements = 1
        if split_mode != SplitMode.TOTAL:
            df[by] = df[by].cat.remove_unused_categories()
            number_of_elements = len(df[by].cat.categories)

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        df.hist(
            column=[variable],
            by=by,
            bins=10,
            log=False,
            sharex=False,
            sharey=False,
            layout=self.__get_plot_layout(number_of_elements),
            ax=ax,
        )

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def __update_distribution_plot(self):
        variable = self.ui.variableSelector.currentText()
        selected_factor = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        x = None
        if self.ui.radioButtonSplitByAnimal.isChecked():
            split_mode = SplitMode.ANIMAL
            x = "Animal"
        elif self.ui.radioButtonSplitByRun.isChecked():
            split_mode = SplitMode.RUN
            x = "Run"
        elif self.ui.radioButtonSplitByFactor.isChecked():
            split_mode = SplitMode.FACTOR
            x = selected_factor

        df = Manager.data.get_current_df(
            variables=[variable],
            split_mode=split_mode,
            selected_factor=selected_factor,
            dropna=False,
        )

        if split_mode != SplitMode.TOTAL:
            df[x] = df[x].cat.remove_unused_categories()

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        if self.ui.radioButtonViolin.isChecked():
            sns.violinplot(data=df, x=x, y=variable, ax=ax)
        else:
            sns.boxplot(data=df, x=x, y=variable, gap=0.1, ax=ax)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def __update_normality_plot(self):
        variable = self.ui.variableSelector.currentText()
        selected_factor = self.ui.factorSelector.currentText()

        split_mode = SplitMode.TOTAL
        by = None
        if self.ui.radioButtonSplitByAnimal.isChecked():
            split_mode = SplitMode.ANIMAL
            by = "Animal"
        elif self.ui.radioButtonSplitByRun.isChecked():
            split_mode = SplitMode.RUN
            by = "Run"
        elif self.ui.radioButtonSplitByFactor.isChecked():
            split_mode = SplitMode.FACTOR
            by = selected_factor

        df = Manager.data.get_current_df(
            variables=[variable],
            split_mode=split_mode,
            selected_factor=selected_factor,
            dropna=True,
        )

        if split_mode != SplitMode.TOTAL:
            df[by] = df[by].cat.remove_unused_categories()

        self.ui.canvas.clear(False)

        match split_mode:
            case SplitMode.ANIMAL:
                animals = df["Animal"].unique()
                nrows, ncols = self.__get_plot_layout(len(animals))
                for index, animal in enumerate(animals):
                    ax = self.ui.canvas.figure.add_subplot(nrows, ncols, index + 1)
                    pg.qqplot(df[df["Animal"] == animal][variable], dist="norm", ax=ax)
                    ax.set_title(f"Animal: {animal}")
            case SplitMode.FACTOR:
                groups = df[selected_factor].unique()
                nrows, ncols = self.__get_plot_layout(len(groups))
                for index, group in enumerate(groups):
                    # TODO: NaN check
                    if group != group:
                        continue
                    ax = self.ui.canvas.figure.add_subplot(nrows, ncols, index + 1)
                    pg.qqplot(df[df[selected_factor] == group][variable], dist="norm", ax=ax)
                    ax.set_title(group)
            case SplitMode.RUN:
                runs = df["Run"].unique()
                nrows, ncols = self.__get_plot_layout(len(runs))
                for index, run in enumerate(runs):
                    ax = self.ui.canvas.figure.add_subplot(nrows, ncols, index + 1)
                    pg.qqplot(df[df["Run"] == run][variable], dist="norm", ax=ax)
                    ax.set_title(f"Run: {run}")
            case SplitMode.TOTAL:
                ax = self.ui.canvas.figure.add_subplot(1, 1, 1)
                pg.qqplot(df[variable], dist="norm", ax=ax)
                ax.set_title("Total")

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def __get_plot_layout(self, number_of_elements: int):
        if number_of_elements == 1:
            return 1, 1
        elif number_of_elements == 2:
            return 1, 2
        elif number_of_elements <= 4:
            return 2, 2
        else:
            return round(number_of_elements / 3) + 1, 3

    def __add_report(self):
        tmp_file = QTemporaryFile(f"{QDir.tempPath()}/XXXXXX.pdf", self)
        if tmp_file.open():
            self.ui.canvas.figure.savefig(tmp_file.fileName())
            Manager.messenger.broadcast(AddToReportMessage(self, [tmp_file.fileName()]))
