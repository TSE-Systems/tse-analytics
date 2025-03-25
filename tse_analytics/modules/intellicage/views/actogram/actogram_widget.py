import numpy as np
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from pyqttoast import ToastPreset

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.split_mode_selector import SplitModeSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class ActogramWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Actogram"

        self.datatable = datatable
        self.split_mode = SplitMode.ANIMAL
        self.selected_factor_name = ""

        # Setup toolbar
        toolbar = QToolBar(
            "Data Plot Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables)
        toolbar.addWidget(self.variableSelector)

        split_mode_selector = SplitModeSelector(toolbar, self.datatable, self._split_mode_callback)
        toolbar.addWidget(split_mode_selector)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.canvas = FigureCanvasQTAgg(None)
        self.layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

    def _split_mode_callback(self, mode: SplitMode, factor_name: str | None):
        self.split_mode = mode
        self.selected_factor_name = factor_name

    def _update(self):
        if self.split_mode == SplitMode.FACTOR and self.selected_factor_name == "":
            make_toast(
                self,
                self.title,
                "Please select a factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        self._update_distribution_plot()

    def _update_distribution_plot(self):
        variable = self.variableSelector.get_selected_variable()

        match self.split_mode:
            case SplitMode.ANIMAL:
                x = "Animal"
            case SplitMode.RUN:
                x = "Run"
            case SplitMode.FACTOR:
                x = self.selected_factor_name
            case _:
                x = None

        df = self.datatable.get_preprocessed_df(
            variables={variable.name: variable},
            split_mode=self.split_mode,
            selected_factor_name=self.selected_factor_name,
            dropna=False,
        )

        if self.split_mode != SplitMode.TOTAL and self.split_mode != SplitMode.RUN:
            df[x] = df[x].cat.remove_unused_categories()

        settings = self.datatable.dataset.binning_settings.time_cycles_settings

        def filter_method(x):
            # return True if Dark cycle
            return not settings.light_cycle_start <= x.time() < settings.dark_cycle_start

        # is_dark = df["DateTime"].apply(filter_method).to_numpy()
        # activity = np.ones(len(is_dark), dtype="int")
        # ca = CycleAnalyzer(df["DateTime"].to_numpy(), activity, is_dark)
        #
        # self.layout.removeWidget(self.canvas)
        # self.canvas.figure.clear()
        # self.canvas.draw()
        # plt.close(self.canvas.figure)
        #
        # data = generate_data()
        #
        # # Prepare input arrays for CycleAnalyzer.
        # # When working with InfluxDB, same arrays must be selected using a DBQuery instance.
        # timestamps = data["time"]  # timestamps of measurements
        # values = data["value"]  # activity values
        # nights = data['is_night'] # night activity markers
        # ca = CycleAnalyzer(timestamps, values, nights)
        #
        # figure = ca.plot_actogram()

        # self.canvas = FigureCanvasQTAgg(figure)
        # self.canvas.updateGeometry()
        # self.canvas.draw()
        # self.layout.addWidget(self.canvas)

    def _add_report(self):
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
