import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_episodes_plot_widget_ui import (
    Ui_DrinkFeedEpisodesPlotWidget,
)


class DrinkFeedIntervalsPlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_DrinkFeedEpisodesPlotWidget()
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
        df = self.df
        # df = self.df.groupby(["Bin"], dropna=False, observed=False).mean(numeric_only=True)

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        sns.barplot(data=df, x="Bin", y=selected_variable, errorbar="se", ax=ax)
        ax.set_xlabel("Time [bin]")
        unit = "g" if "Feed" in selected_variable else "ml"
        ax.set_ylabel(f"Meal size [{unit}]")

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
