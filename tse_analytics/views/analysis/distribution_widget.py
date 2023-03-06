from typing import Optional

import seaborn as sns
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtWidgets import QLabel, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_datatools.data.variable import Variable


class DistributionWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.help_path = "docs/distribution.md"

        self.variable = ""
        self.variable_selector = VariableSelector()
        self.variable_selector.currentTextChanged.connect(self.__variable_changed)
        self.toolbar.addWidget(QLabel("Variable: "))
        self.toolbar.addWidget(self.variable_selector)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)

        self.layout().addWidget(NavigationToolbar2QT(self.canvas, self))
        self.layout().addWidget(self.canvas)

    def clear(self):
        self.variable_selector.clear()
        self.ax.clear()

    def update_variables(self, variables: dict[str, Variable]):
        self.variable_selector.set_data(variables)

    def __variable_changed(self, variable: str):
        self.variable = variable

    def _analyze(self):
        if Manager.data.selected_dataset is None or (
            Manager.data.grouping_mode == GroupingMode.FACTORS and Manager.data.selected_factor is None):
            return

        df = Manager.data.selected_dataset.active_df

        self.ax.clear()

        # sns.boxplot(data=df, x="Group", y=self.variable, ax=self.ax, color="green")
        x = Manager.data.selected_factor.name if Manager.data.grouping_mode == GroupingMode.FACTORS else "Animal"
        sns.violinplot(data=df, x=x, y=self.variable, ax=self.ax)

        self.canvas.figure.tight_layout()
        self.canvas.draw()
