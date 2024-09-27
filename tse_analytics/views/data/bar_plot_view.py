import pandas as pd
import seaborn as sns
from PySide6.QtWidgets import QVBoxLayout, QWidget
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from tse_analytics.core.data.shared import Factor, SplitMode
from tse_analytics.core.helper import get_html_image
from tse_analytics.core.manager import Manager


class BarPlotView(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._df: pd.DataFrame | None = None
        self._variable = ""
        self._split_mode = SplitMode.ANIMAL
        self._selected_factor: Factor | None = None
        self._error_type = "sd"
        self._display_errors = False

        self.canvas = FigureCanvasQTAgg(None)

    def set_data(self, df: pd.DataFrame):
        self._df = df
        self._update_plot()

    def set_variable(self, variable: str, update: bool):
        self._variable = variable
        if update:
            self._update_plot()

    def set_grouping_mode(self, grouping_mode: SplitMode, selected_factor: Factor):
        self._split_mode = grouping_mode
        self._selected_factor = selected_factor

    def set_display_errors(self, state: bool):
        self._display_errors = state
        self._update_plot()

    def set_error_type(self, error_type: str):
        self._error_type = error_type
        self._update_plot()

    def clear_plot(self):
        self._df = None
        self._variable = None
        self._display_errors = False

    def _update_plot(self):
        if (
            self._df is None
            or self._variable == ""
            or (self._split_mode == SplitMode.FACTOR and self._selected_factor is None)
            or not Manager.data.binning_params.apply
        ):
            return

        self.layout().removeWidget(self.canvas)
        self.canvas.figure.clear()
        self.canvas.draw()
        plt.close(self.canvas.figure)

        if not self._df.empty:
            match self._split_mode:
                case SplitMode.ANIMAL:
                    x_name = "Animal"
                case SplitMode.FACTOR:
                    x_name = self._selected_factor.name
                case SplitMode.RUN:
                    x_name = "Run"
                case _:
                    x_name = None

            if self._split_mode != SplitMode.TOTAL and self._split_mode != SplitMode.RUN:
                self._df[x_name] = self._df[x_name].cat.remove_unused_categories()

            facet_grid = sns.catplot(
                data=self._df,
                x=x_name,
                y=self._variable,
                col="Bin",
                kind="bar",
                errorbar=self._error_type if self._display_errors else None,
            )
            facet_grid.set_xticklabels(rotation=75)
            # facet_grid.set_titles("{col_name}")
            self.canvas = FigureCanvasQTAgg(facet_grid.figure)
            self.canvas.updateGeometry()
            self.canvas.draw()
            self.layout().addWidget(self.canvas)

    def get_report(self) -> str:
        return get_html_image(self.canvas.figure)
