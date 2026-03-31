import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.data.shared import Variable
from tse_analytics.core.utils import get_html_image_from_figure


class BarPlotView(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.datatable: Datatable | None = None
        self._df: pd.DataFrame | None = None
        self._variable: Variable | None = None
        self._grouping_settings: GroupingSettings | None = None
        self._error_type = "se"
        self._display_errors = False

        self.canvas = FigureCanvasQTAgg(None)

    def refresh_data(
        self,
        datatable: Datatable,
        df: pd.DataFrame,
        variable: Variable,
        grouping_settings: GroupingSettings,
        display_errors: bool,
        error_type: str | None,
    ) -> None:
        self.datatable = datatable
        self._df = df
        self._variable = variable
        self._grouping_settings = grouping_settings
        self._display_errors = display_errors
        self._error_type = error_type

        self._update_plot()

    def _update_plot(self):
        self.layout().removeWidget(self.canvas)
        self.canvas.figure.clear()
        self.canvas.draw()
        plt.close(self.canvas.figure)

        if (
            self._df is None
            or self._variable is None
            or (self._grouping_settings.mode == GroupingMode.FACTOR and self._grouping_settings.factor_name == "")
        ):
            return

        if not self._df.empty:
            match self._grouping_settings.mode:
                case GroupingMode.ANIMAL:
                    x_name = "Animal"
                case GroupingMode.FACTOR:
                    x_name = self._grouping_settings.factor_name
                case GroupingMode.RUN:
                    x_name = "Run"
                case _:
                    x_name = None

            if self._grouping_settings.mode != GroupingMode.TOTAL and self._grouping_settings.mode != GroupingMode.RUN:
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
        return get_html_image_from_figure(self.canvas.figure)
