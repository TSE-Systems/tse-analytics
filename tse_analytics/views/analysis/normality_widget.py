from typing import Optional

import pandas as pd
import pingouin as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout
import scipy.stats as stats

from tse_analytics.core.manager import Manager


class NormalityWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.canvas = FigureCanvas(Figure(figsize=(5.0, 4.0), dpi=100))

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

    def analyze(self, df: pd.DataFrame, variable: str):
        if len(Manager.data.selected_groups) == 0:
            return

        self.clear()

        unique_groups = df['Group'].unique()
        ncols = 2
        nrows = len(unique_groups) // 2 + (len(unique_groups) % 2 > 0)
        for index, group in enumerate(unique_groups):
            ax = self.canvas.figure.add_subplot(nrows, ncols, index+1)
            # stats.probplot(df[df['Group'] == group][variable], dist="norm", plot=ax)
            pg.qqplot(df[df['Group'] == group][variable], dist='norm', ax=ax)
            ax.set_title(group)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        self.canvas.figure.clear()
