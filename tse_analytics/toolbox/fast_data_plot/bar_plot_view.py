import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from tse_analytics.core import color_manager
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
                    by = "Animal"
                    # Cleaning
                    self._df[by] = self._df[by].cat.remove_unused_categories()
                    palette = color_manager.get_animal_to_color_dict(self.datatable.dataset.animals)
                case GroupingMode.RUN:
                    by = "Run"
                    palette = color_manager.get_run_to_color_dict(self.datatable.dataset.runs)
                case GroupingMode.FACTOR:
                    by = self._grouping_settings.factor_name
                    palette = color_manager.get_level_to_color_dict(self.datatable.dataset.factors[by])
                case _:
                    by = None
                    palette = color_manager.colormap_name

            # TODO: workaround for issue with nullable Float64
            # self._df[self._variable.name] = self._df[self._variable.name].astype(float)

            if (
                self._grouping_settings.mode == GroupingMode.ANIMAL
                or self._grouping_settings.mode == GroupingMode.FACTOR
            ):
                # TODO: temporary fix for issue with broken categories offset when using pandas 3.0
                self._df.sort_values(by, inplace=True)
                self._df[by] = self._df[by].astype("string")

            facet_grid = sns.catplot(
                data=self._df,
                x=by,
                y=self._variable.name,
                hue=by,
                palette=palette,
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
