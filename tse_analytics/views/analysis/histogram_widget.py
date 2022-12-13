import os.path
from typing import Optional

from PySide6.QtWidgets import QWidget, QToolBar, QPushButton

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget


class HistogramWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.layout.addWidget(self._get_toolbar())

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)

        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

    def clear(self):
        self.ax.clear()

    def dataset_changed(self):
        pass

    def _get_plot_layout(self, number_of_elements: int):
        if number_of_elements == 1:
            return None
        elif number_of_elements <= 3:
            return number_of_elements, 1
        elif number_of_elements == 4:
            return 2, 2
        else:
            return round(number_of_elements / 3) + 1, 3

    def _analyze(self):
        if Manager.data.selected_dataset is None or len(Manager.data.selected_variables) == 0:
            return

        self.ax.clear()

        df = Manager.data.selected_dataset.original_df
        selected_variables = Manager.data.selected_variables
        columns = [item.name for item in selected_variables]

        df.hist(
            column=columns,
            bins=50,
            sharex=False,
            sharey=False,
            layout=self._get_plot_layout(len(selected_variables)),
            ax=self.ax,
        )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    @property
    def help_content(self) -> Optional[str]:
        path = "docs/histogram.md"
        if os.path.exists(path):
            with open(path, "r") as file:
                return file.read().rstrip()

    def _get_toolbar(self) -> QToolBar:
        toolbar = super()._get_toolbar()

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self._analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
