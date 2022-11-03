from typing import Optional

import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout
import seaborn as sns

from tse_analytics.core.manager import Manager


class DistributionWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.canvas = FigureCanvas(Figure(figsize=(5.0, 4.0), dpi=100))
        self.ax = self.canvas.figure.subplots()

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

    def analyze(self, df: pd.DataFrame, variable: str):
        if len(Manager.data.selected_groups) == 0:
            return

        self.ax.clear()

        sns.boxplot(x='Group', y=variable, data=df, color='#99c2a2', ax=self.ax)
        # sns.swarmplot(x="Group", y=variable, data=df, color='#7d0013', ax=self.ax, size=2)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        self.ax.clear()
