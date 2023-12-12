from typing import Optional

import pandas as pd
import seaborn as sns
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from tse_analytics.core.manager import Manager
from tse_datatools.analysis.grouping_mode import GroupingMode


class BarPlotView(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._df: Optional[pd.DataFrame] = None
        self._variable: str = ""
        self._display_errors = False

        self.canvas: Optional[FigureCanvasQTAgg] = FigureCanvasQTAgg(None)

    def set_data(self, df: pd.DataFrame):
        self._df = df
        self._update_plot()

    def set_variable(self, variable: str, update: bool):
        self._variable = variable
        if update:
            self._update_plot()

    def set_display_errors(self, state: bool):
        self._display_errors = state
        self._update_plot()

    def clear_plot(self):
        self._df = None
        self._variable = None
        self._display_errors = False

    def _update_plot(self):
        if (
            self._df is None
            or self._variable == ""
            or (Manager.data.grouping_mode == GroupingMode.FACTORS and Manager.data.selected_factor is None)
            or not Manager.data.binning_params.apply
        ):
            return

        if self.canvas is not None:
            self.layout().removeWidget(self.canvas)
            self.canvas.figure.clear()
            self.canvas.draw()
            plt.close(self.canvas.figure)

        if not self._df.empty:
            match Manager.data.grouping_mode:
                case GroupingMode.FACTORS:
                    x_name = Manager.data.selected_factor.name
                case GroupingMode.RUNS:
                    x_name = "Run"
                case _:
                    x_name = "Animal"

            self._df[x_name] = self._df[x_name].cat.remove_unused_categories()

            faced_grid = sns.catplot(
                x=x_name,
                y=self._variable,
                col="Bin",
                data=self._df,
                kind="bar",
                errorbar=("ci", 95) if self._display_errors else None,
            )
            faced_grid.set_xticklabels(rotation=90)
            faced_grid.set_titles("{col_name}")
            self.canvas = FigureCanvasQTAgg(faced_grid.figure)
            self.canvas.updateGeometry()
            self.canvas.draw()
            self.layout().addWidget(self.canvas)
