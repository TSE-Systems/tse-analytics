from dataclasses import dataclass

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QSpinBox, QToolBar, QVBoxLayout, QWidget, QWidgetAction

from tse_analytics.core import color_manager, messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.helper import normalize_nd_array
from tse_analytics.core.plotting.actogram_utils import dataframe_to_actogram, plot_enhanced_actogram
from tse_analytics.core.utils import get_h_spacer_widget, get_html_image_from_figure, time_to_float
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class ActogramWidgetSettings:
    selected_variable: str = None
    bins_per_hour: int = 6


class ActogramWidget(QWidget):
    """Widget for visualizing activity patterns over time in a double-plotted actogram format.

    An actogram is a graphical representation of activity data over multiple days,
    typically used in chronobiology to visualize circadian rhythms. This widget
    creates a double-plotted actogram where each row represents two consecutive days,
    allowing for better visualization of activity patterns that cross midnight.
    """

    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: ActogramWidgetSettings = settings.value(self.__class__.__name__, ActogramWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Actogram"

        self.datatable = datatable

        # Setup toolbar
        self.toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        self.toolbar.addSeparator()

        self.variableSelector = VariableSelector(self.toolbar)
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        self.toolbar.addWidget(self.variableSelector)

        self.toolbar.addWidget(QLabel("Bins per hour:"))
        self.bins_spin_box = QSpinBox(
            self.toolbar,
            minimum=1,
            maximum=60,
            singleStep=1,
            value=self._settings.bins_per_hour,
        )
        self.toolbar.addWidget(self.bins_spin_box)

        # Insert toolbar to the widget
        self._layout.addWidget(self.toolbar)

        self.canvas = FigureCanvasQTAgg(None)
        self._layout.addWidget(self.canvas)

        self.spacer_action = QWidgetAction(self.toolbar)
        self.spacer_action.setDefaultWidget(get_h_spacer_widget(self.toolbar))
        self.toolbar.addAction(self.spacer_action)

        self.toolbar.addAction("Add to Report").triggered.connect(self._add_report)
        self._add_plot_toolbar()

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            ActogramWidgetSettings(
                self.variableSelector.currentText(),
                self.bins_spin_box.value(),
            ),
        )

    def _add_plot_toolbar(self):
        """Add a matplotlib navigation toolbar to the widget.

        Creates and adds a matplotlib navigation toolbar that provides
        functionality like zooming, panning, and saving the plot.
        """
        self.plot_toolbar_action = QWidgetAction(self.toolbar)
        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        self.plot_toolbar_action.setDefaultWidget(plot_toolbar)
        self.toolbar.insertAction(self.spacer_action, self.plot_toolbar_action)

    def _update(self):
        """Update the actogram visualization.

        Gets the selected variable and temporal resolution, processes the data,
        and creates a new actogram visualization. This method is called when
        the user changes settings or clicks the Update button.
        """
        variable = self.variableSelector.get_selected_variable()

        columns = ["Animal", "DateTime", variable.name]
        df = self.datatable.get_filtered_df(columns)

        settings = self.datatable.dataset.binning_settings.time_cycles_settings

        bins_per_hour = self.bins_spin_box.value()

        # Convert DataFrame to actogram format
        activity_array, unique_days = dataframe_to_actogram(df, variable, 24 * bins_per_hour)

        # Normalize data
        activity_array = normalize_nd_array(activity_array)

        # Create day labels
        day_labels = [d.strftime("%Y-%m-%d") for d in unique_days]

        if settings.dark_cycle_start < settings.light_cycle_start:
            periods = [
                {
                    "start": time_to_float(settings.dark_cycle_start),
                    "end": time_to_float(settings.light_cycle_start),
                    "color": "gray",
                    "alpha": 0.2,
                }
            ]
        else:
            periods = [
                {
                    "start": 0,
                    "end": time_to_float(settings.light_cycle_start),
                    "color": "gray",
                    "alpha": 0.2,
                },
                {
                    "start": time_to_float(settings.dark_cycle_start),
                    "end": 24,
                    "color": "gray",
                    "alpha": 0.2,
                },
            ]

        # Plot double actogram
        fig, ax = plot_enhanced_actogram(
            activity_array,
            day_labels,
            binsize=1 / bins_per_hour,
            highlight_periods=periods,
            bar_color=color_manager.get_color_hex(0),
            title=f"Actogram - {variable.name}",
        )

        canvas = FigureCanvasQTAgg(fig)
        # canvas.updateGeometry()
        canvas.draw()
        self._layout.replaceWidget(self.canvas, canvas)

        # Cleanup
        self.canvas.figure.clear()
        plt.close(self.canvas.figure)
        # gc.collect()

        self.canvas = canvas

        # Assign canvas to PlotToolbar
        self.toolbar.removeAction(self.plot_toolbar_action)
        self._add_plot_toolbar()

    def _add_report(self):
        """Add the current actogram to the dataset report.

        Converts the current actogram figure to HTML and adds it to the
        dataset's report. Also broadcasts a message to notify the application
        that content has been added to the report.
        """
        self.datatable.dataset.report += get_html_image_from_figure(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
