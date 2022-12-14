import os.path
from typing import Optional

import seaborn as sns
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtWidgets import QLabel, QPushButton, QToolBar, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_datatools.data.variable import Variable


class DistributionWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.variable_selector = VariableSelector()
        self.variable_selector.currentTextChanged.connect(self.__variable_changed)
        self.variable = ""

        self.layout().addWidget(self._get_toolbar())

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)

        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

    def clear(self):
        self.variable_selector.clear()
        self.ax.clear()

    def update_variables(self, variables: dict[str, Variable]):
        self.variable_selector.set_data(variables)

    def __variable_changed(self, variable: str):
        self.variable = variable

    def __analyze(self):
        if Manager.data.selected_dataset is None:
            return

        df = Manager.data.selected_dataset.original_df

        self.ax.clear()

        sns.boxplot(data=df, x="Group", y=self.variable, ax=self.ax, color="green")
        sns.violinplot(data=df, x="Group", y=self.variable, ax=self.ax)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    @property
    def help_content(self) -> Optional[str]:
        path = "docs/distribution.md"
        if os.path.exists(path):
            with open(path, "r") as file:
                return file.read().rstrip()
        return None

    def _get_toolbar(self) -> QToolBar:
        toolbar = super()._get_toolbar()

        toolbar.addWidget(QLabel("Variable: "))
        toolbar.addWidget(self.variable_selector)

        button = QPushButton("Analyze")
        button.clicked.connect(self.__analyze)
        toolbar.addWidget(button)

        return toolbar
