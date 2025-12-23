import pandas as pd
import seaborn.objects as so
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import color_manager
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_bin_data import DrinkFeedBinData
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_raw_data import DrinkFeedRawData
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.variable_selector import VariableSelector


class IntervalsPlotWidget(QWidget):
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
        self.drinkfeed_data: DrinkFeedBinData | DrinkFeedRawData | None = None

    def set_data(self, df: pd.DataFrame, drinkfeed_data: DrinkFeedBinData | DrinkFeedRawData) -> None:
        self.df = df
        self.drinkfeed_data = drinkfeed_data
        self.variableSelector.set_data(drinkfeed_data.variables)
        self._update_plot()

    def _variable_changed(self, variable: str):
        self._update_plot()

    def _update_plot(self):
        if self.df is None:
            self.canvas.clear(True)
            return

        selected_variable = self.variableSelector.currentText()
        df = self.df

        unit = "g" if "Feed" in selected_variable else "ml"

        self.canvas.clear(False)
        (
            so
            .Plot(df, x="Bin", y=selected_variable, color="Animal")
            .add(so.Bars())
            .scale(color=color_manager.get_animal_to_color_dict(self.drinkfeed_data.dataset.animals))
            .label(
                x="Time [bin]",
                y=f"Meal size [{unit}]",
            )
            .on(self.canvas.figure)
            .plot(True)
        )
        self.canvas.figure.tight_layout()
        self.canvas.draw()
