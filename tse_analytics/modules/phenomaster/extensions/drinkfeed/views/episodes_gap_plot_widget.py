import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QToolBar, QVBoxLayout, QWidget

from tse_analytics.core.data.shared import Variable
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.variable_selector import VariableSelector


class EpisodesGapPlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.currentTextChanged.connect(self._variable_changed)
        toolbar.addWidget(self.variableSelector)

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self._layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        self.df: pd.DataFrame | None = None

    def set_data(self, df: pd.DataFrame, variables: dict[str, Variable]) -> None:
        self.df = df
        self.variableSelector.set_data(variables)
        self._update_plot()

    def _variable_changed(self, variable: str):
        self._update_plot()

    def _update_plot(self):
        if self.df is None:
            self.canvas.clear(True)
            return

        selected_variable = self.variableSelector.currentText()
        df = self.df[self.df["Sensor"] == selected_variable]

        df["Gap"] = df["Gap"] / pd.Timedelta(minutes=1)

        self.canvas.clear(False)
        ax = self.canvas.figure.add_subplot(111)

        sns.stripplot(data=df, x="Gap", y="Animal", hue="Animal", log_scale=True, jitter=False, ax=ax)
        ax.set_xlabel("Intermeal interval [min]")
        ax.set_xticks([1, 10, 100, 1000])
        ax.grid(True, which="minor", axis="x", ls="-")

        self.canvas.figure.tight_layout()
        self.canvas.draw()
