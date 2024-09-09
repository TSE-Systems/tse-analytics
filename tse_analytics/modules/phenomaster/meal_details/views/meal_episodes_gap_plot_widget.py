import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.meal_details.views.meal_episodes_plot_widget_ui import Ui_MealEpisodesPlotWidget


class MealEpisodesGapPlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_MealEpisodesPlotWidget()
        self.ui.setupUi(self)

        plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count() - 1, plot_toolbar)

        self.ui.variableSelector.currentTextChanged.connect(self._variable_changed)

        self.df: pd.DataFrame | None = None

    def set_data(self, df: pd.DataFrame, variables: dict[str, Variable]) -> None:
        self.df = df
        self.ui.variableSelector.set_data(variables)
        self._update_plot()

    def _variable_changed(self, variable: str):
        self._update_plot()

    def _update_plot(self):
        if self.df is None:
            self.ui.canvas.clear(True)
            return

        selected_variable = self.ui.variableSelector.currentText()
        df = self.df[self.df["Sensor"] == selected_variable]

        df["Gap"] = df["Gap"] / pd.Timedelta(minutes=1)

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        sns.stripplot(data=df, x="Gap", y="Animal", hue="Animal", log_scale=True, jitter=False, ax=ax)
        ax.set_xlabel("Intermeal interval [min]")
        ax.set_xticks([1, 10, 100, 1000])
        ax.grid(True, which="minor", axis="x", ls="-")

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
