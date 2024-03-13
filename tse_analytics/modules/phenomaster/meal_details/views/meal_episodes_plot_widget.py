import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.meal_details.views.meal_episodes_plot_widget_ui import Ui_MealEpisodesPlotWidget


class MealEpisodesPlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_MealEpisodesPlotWidget()
        self.ui.setupUi(self)

        self.ui.horizontalLayout.insertWidget(
            self.ui.horizontalLayout.count() - 1, NavigationToolbar2QT(self.ui.canvas, self)
        )

        self.df: pd.DataFrame | None = None

    def set_data(self, df: pd.DataFrame):
        if df is None:
            self.ui.canvas.clear(True)
            return

        self.df = df

        data = df
        data["Offset"] = data["Offset"] / pd.Timedelta(hours=1)
        data["Gap"] = data["Gap"] / pd.Timedelta(minutes=1)

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.subplots(2)

        sns.stripplot(
            data=data,
            x="Offset",
            y="Animal",
            hue="Sensor",
            ax=ax[0]
        )
        ax[0].set_xlabel("Offset [hours]")

        sns.stripplot(
            data=data,
            x="Gap",
            y="Animal",
            hue="Sensor",
            log_scale=True,
            ax=ax[1]
        )
        ax[1].set_xlabel("Intermeal interval [min]")
        ax[1].set_xticks([1, 10, 100, 1000])
        ax[1].grid(True, which="minor", axis="x", ls="-")

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
