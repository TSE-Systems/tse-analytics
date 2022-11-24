from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QPushButton, QLabel, QComboBox

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import seaborn as sns

from tse_analytics.core.manager import Manager
from tse_datatools.data.variable import Variable


class DistributionWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.variable_combo_box = QComboBox(self)
        self.variable = ''

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self._get_toolbar())

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)

        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

    def clear(self):
        self.variable_combo_box.clear()
        self.ax.clear()

    def update_variables(self, variables: dict[str, Variable]):
        self.variable = ''
        self.variable_combo_box.clear()
        self.variable_combo_box.addItems(variables)
        self.variable_combo_box.setCurrentText(self.variable)

    def _variable_changed(self, variable: str):
        self.variable = variable

    def _analyze(self):
        if Manager.data.selected_dataset is None:
            return

        df = Manager.data.selected_dataset.original_df

        self.ax.clear()

        sns.boxplot(data=df, x='Group', y=self.variable, ax=self.ax, color='green')
        sns.violinplot(data=df, x="Group", y=self.variable, ax=self.ax)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _get_toolbar(self) -> QToolBar:
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        label = QLabel("Variable: ")
        toolbar.addWidget(label)

        self.variable_combo_box.currentTextChanged.connect(self._variable_changed)
        toolbar.addWidget(self.variable_combo_box)

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self._analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
