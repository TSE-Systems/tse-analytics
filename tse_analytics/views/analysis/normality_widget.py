from typing import Optional

import pingouin as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtWidgets import QLabel, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_datatools.data.variable import Variable


class NormalityWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.help_path = "docs/normality.md"

        self.variable = ""
        self.variable_selector = VariableSelector()
        self.variable_selector.currentTextChanged.connect(self.__variable_changed)
        self.toolbar.addWidget(QLabel("Variable: "))
        self.toolbar.addWidget(self.variable_selector)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.canvas = FigureCanvasQTAgg(figure)

        self.layout().addWidget(NavigationToolbar2QT(self.canvas, self))
        self.layout().addWidget(self.canvas)

    def clear(self):
        self.canvas.figure.clear()

    def update_variables(self, variables: dict[str, Variable]):
        self.variable_selector.set_data(variables)

    def __variable_changed(self, variable: str):
        self.variable = variable

    def _analyze(self):
        if Manager.data.selected_dataset is None:
            return

        df = Manager.data.selected_dataset.original_df

        self.clear()

        unique_groups = df["Group"].unique()
        ncols = 2
        nrows = len(unique_groups) // 2 + (len(unique_groups) % 2 > 0)
        for index, group in enumerate(unique_groups):
            ax = self.canvas.figure.add_subplot(nrows, ncols, index + 1)
            # stats.probplot(df[df['Group'] == group][variable], dist="norm", plot=ax)
            pg.qqplot(df[df["Group"] == group][self.variable], dist="norm", ax=ax)
            ax.set_title(group)

        self.canvas.figure.tight_layout()
        self.canvas.draw()
