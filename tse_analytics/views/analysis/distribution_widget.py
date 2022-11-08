from typing import Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import pandas as pd
import seaborn as sns

from tse_analytics.core.manager import Manager


class DistributionWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)

        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

    def analyze(self, df: pd.DataFrame, variable: str):
        if len(Manager.data.selected_groups) == 0:
            return

        self.ax.clear()

        sns.boxplot(data=df, x='Group', y=variable, ax=self.ax, color='green')
        sns.violinplot(data=df, x="Group", y=variable, ax=self.ax)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        self.ax.clear()
