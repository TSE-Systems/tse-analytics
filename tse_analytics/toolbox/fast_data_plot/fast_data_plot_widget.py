from PySide6.QtWidgets import QVBoxLayout, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.toolbox.fast_data_plot.fast_bar_plot_widget import FastBarPlotWidget
from tse_analytics.toolbox.fast_data_plot.fast_line_plot_widget import FastLinePlotWidget
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin


@toolbox_plugin(category="Data", label="Fast Plot", icon=":/icons/plot.png", order=1)
class FastDataPlotWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        if "Timedelta" in datatable.df.columns:
            widget = FastLinePlotWidget(datatable, self)
        else:
            widget = FastBarPlotWidget(datatable, self)

        self._layout.addWidget(widget)
