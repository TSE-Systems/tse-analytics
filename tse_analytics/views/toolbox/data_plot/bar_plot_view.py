import pandas as pd
import seaborn as sns
from PySide6.QtWidgets import QVBoxLayout, QWidget
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Factor, SplitMode, Variable
from tse_analytics.core.utils import get_html_image


class BarPlotView(QWidget):
    """Widget for displaying data as a bar plot.

    This widget creates and displays bar plots using seaborn's catplot functionality.
    It supports different grouping options and can display error bars.

    Attributes:
        datatable: The datatable containing the data being visualized.
        canvas: The matplotlib canvas where the bar plot is drawn.
        _df: The DataFrame containing the processed data for plotting.
        _variable: The variable being visualized.
        _split_mode: The mode for splitting/grouping the data.
        _selected_factor: The selected factor when split_mode is FACTOR.
        _error_type: The type of error bars to display ("se" or "sd").
        _display_errors: Whether to display error bars.
    """

    def __init__(self, parent: QWidget):
        """Initialize the bar plot view.

        Args:
            parent: The parent widget.
        """
        super().__init__(parent)

        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.datatable: Datatable | None = None
        self._df: pd.DataFrame | None = None
        self._variable: Variable | None = None
        self._split_mode = SplitMode.ANIMAL
        self._selected_factor: Factor | None = None
        self._error_type = "se"
        self._display_errors = False

        self.canvas = FigureCanvasQTAgg(None)

    def refresh_data(
        self,
        datatable: Datatable,
        df: pd.DataFrame,
        variable: Variable,
        split_mode: SplitMode,
        selected_factor: Factor,
        display_errors: bool,
        error_type: str,
    ) -> None:
        """Update the bar plot with new data and settings.

        Args:
            datatable: The datatable containing the data being visualized.
            df: The DataFrame containing the processed data for plotting.
            variable: The variable to visualize.
            split_mode: The mode for splitting/grouping the data.
            selected_factor: The selected factor when split_mode is FACTOR.
            display_errors: Whether to display error bars.
            error_type: The type of error bars to display ("se" or "sd").
        """
        self.datatable = datatable
        self._df = df
        self._variable = variable
        self._split_mode = split_mode
        self._display_errors = display_errors
        self._selected_factor = selected_factor
        self._error_type = error_type

        self._update_plot()

    def _update_plot(self):
        """Update the bar plot visualization.

        This method creates a new bar plot using seaborn's catplot functionality
        based on the current data and settings. It handles different grouping options
        and can display error bars.
        """
        self.layout().removeWidget(self.canvas)
        self.canvas.figure.clear()
        self.canvas.draw()
        plt.close(self.canvas.figure)

        if (
            self._df is None
            or self._variable is None
            or (self._split_mode == SplitMode.FACTOR and self._selected_factor is None)
            or not self.datatable.dataset.binning_settings.apply
            or (
                self.datatable.dataset.binning_settings.mode == BinningMode.PHASES
                and len(self.datatable.dataset.binning_settings.time_phases_settings.time_phases) == 0
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
        """Get an HTML representation of the current bar plot for reporting.

        Returns:
            HTML string containing the bar plot image.
        """
        return get_html_image(self.canvas.figure)
