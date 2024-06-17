import pingouin as pg
import seaborn as sns
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import GroupingMode
from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.exploration_widget_ui import Ui_ExplorationWidget
from tse_analytics.views.misc.toast import Toast


class ExplorationWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_ExplorationWidget()
        self.ui.setupUi(self)

        self.help_path = "exploration.md"
        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self.__update)

        self.ui.radioButtonDistribution.toggled.connect(lambda: self.ui.groupBoxDistribution.setEnabled(True))
        self.ui.radioButtonHistogram.toggled.connect(lambda: self.ui.groupBoxDistribution.setEnabled(False))
        self.ui.radioButtonDistribution.toggled.connect(lambda: self.ui.groupBoxDistribution.setEnabled(True))
        self.ui.radioButtonNormality.toggled.connect(lambda: self.ui.groupBoxDistribution.setEnabled(False))

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().insertWidget(0, plot_toolbar)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.pushButtonUpdate.setDisabled(message.data is None)
        self.__clear()
        if message.data is not None:
            self.ui.variableSelector.set_data(message.data.variables)
            self.ui.factorSelector.set_data(message.data.factors)

    def __clear(self):
        self.ui.variableSelector.clear()
        self.ui.factorSelector.clear()
        self.ui.canvas.clear(True)

    def __update(self):
        if self.ui.groupBoxSplitBy.isChecked() and self.ui.factorSelector.currentText() == "":
            Toast(text="Please select factor first.", parent=self, duration=2000).show_toast()
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
        by = selected_factor if self.ui.groupBoxSplitBy.isChecked() else "Animal"

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        df = Manager.data.get_current_df(
            variables=[variable],
            grouping_mode=GroupingMode.ANIMALS,
            selected_factor=None,
            dropna=False,
        )
        df[by] = df[by].cat.remove_unused_categories()

        number_of_elements = len(df[by].cat.categories)
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
        x = selected_factor if self.ui.groupBoxSplitBy.isChecked() else "Animal"

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        df = Manager.data.get_current_df(
            variables=[variable],
            grouping_mode=GroupingMode.ANIMALS,
            selected_factor=None,
            dropna=False,
        )
        df[x] = df[x].cat.remove_unused_categories()

        if self.ui.radioButtonViolin.isChecked():
            sns.violinplot(data=df, x=x, y=variable, ax=ax)
        else:
            if selected_factor != "":
                sns.boxplot(data=df, x=x, y=variable, hue=selected_factor, gap=0.1, ax=ax)
            else:
                sns.boxplot(data=df, x=x, y=variable, gap=0.1, ax=ax)

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()

    def __update_normality_plot(self):
        variable = self.ui.variableSelector.currentText()

        selected_factor = self.ui.factorSelector.currentText()
        by = selected_factor if self.ui.groupBoxSplitBy.isChecked() else "Animal"

        self.ui.canvas.clear(False)

        df = Manager.data.get_current_df(
            variables=[variable],
            grouping_mode=GroupingMode.ANIMALS,
            selected_factor=None,
            dropna=False,
        )
        df[by] = df[by].cat.remove_unused_categories()

        if self.ui.groupBoxSplitBy.isChecked():
            groups = df[selected_factor].unique()
            nrows, ncols = self.__get_plot_layout(len(groups))
            for index, group in enumerate(groups):
                # TODO: NaN check
                if group != group:
                    continue
                ax = self.ui.canvas.figure.add_subplot(nrows, ncols, index + 1)
                # stats.probplot(df[df[factor_name] == group][variable], dist="norm", plot=ax)
                pg.qqplot(df[df[selected_factor] == group][variable], dist="norm", ax=ax)
                ax.set_title(group)
        else:
            animals = df["Animal"].unique()
            nrows, ncols = self.__get_plot_layout(len(animals))
            for index, animal in enumerate(animals):
                ax = self.ui.canvas.figure.add_subplot(nrows, ncols, index + 1)
                # stats.probplot(df[df["Animal"] == group][variable], dist="norm", plot=ax)
                pg.qqplot(df[df["Animal"] == animal][variable], dist="norm", ax=ax)
                ax.set_title(animal)

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
