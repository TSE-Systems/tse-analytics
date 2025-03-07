import pandas as pd
import seaborn as sns
from PySide6.QtWidgets import QVBoxLayout, QWidget
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Factor, SplitMode, Variable
from tse_analytics.core.helper import get_html_image


class BarPlotView(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.dataset: Dataset | None = None
        self._df: pd.DataFrame | None = None
        self._variable: Variable | None = None
        self._split_mode = SplitMode.ANIMAL
        self._selected_factor: Factor | None = None
        self._error_type = "se"
        self._display_errors = False

        self.canvas = FigureCanvasQTAgg(None)

    def refresh_data(
        self,
        dataset: Dataset,
        df: pd.DataFrame,
        variable: Variable,
        split_mode: SplitMode,
        selected_factor: Factor,
        display_errors: bool,
        error_type: str,
    ) -> None:
        self.dataset = dataset
        self._df = df
        self._variable = variable
        self._split_mode = split_mode
        self._display_errors = display_errors
        self._selected_factor = selected_factor
        self._error_type = error_type

        self._update_plot()

    def clear_plot(self):
        self._df = None
        self._variable = None
        self._display_errors = False

    def _update_plot(self):
        self.layout().removeWidget(self.canvas)
        self.canvas.figure.clear()
        self.canvas.draw()
        plt.close(self.canvas.figure)

        if (
            self._df is None
            or self._variable is None
            or (self._split_mode == SplitMode.FACTOR and self._selected_factor is None)
            or not self.dataset.binning_settings.apply
            or (
                self.dataset.binning_settings.mode == BinningMode.PHASES
                and len(self.dataset.binning_settings.time_phases_settings.time_phases) == 0
            )
        ):
            return

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
                y=self._variable.name,
                col="Bin",
                kind="bar",
                errorbar=self._error_type if self._display_errors else None,
            )
            facet_grid.set_xticklabels(rotation=90)
            # facet_grid.set_titles("{col_name}")
            self.canvas = FigureCanvasQTAgg(facet_grid.figure)
            self.canvas.updateGeometry()
            self.canvas.draw()
            self.layout().addWidget(self.canvas)

    def get_report(self) -> str:
        return get_html_image(self.canvas.figure)
