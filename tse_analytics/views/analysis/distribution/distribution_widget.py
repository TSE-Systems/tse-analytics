import seaborn as sns
from PySide6.QtGui import QIcon
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QComboBox

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import get_html_image, get_h_spacer_widget
from tse_analytics.core.toaster import make_toast
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.split_mode_selector import SplitModeSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class DistributionWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Distribution"

        self.dataset = dataset
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
        self.variableSelector.set_data(self.dataset.variables)
        toolbar.addWidget(self.variableSelector)

        split_mode_selector = SplitModeSelector(toolbar, self.dataset.factors, self._split_mode_callback)
        toolbar.addWidget(split_mode_selector)

        self.plot_type_combobox = QComboBox(toolbar)
        self.plot_type_combobox.addItems(["Violin plot", "Box plot"])
        toolbar.addWidget(self.plot_type_combobox)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
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

        df = self.dataset.get_current_df(
            variables={variable.name: variable},
            split_mode=self.split_mode,
            selected_factor_name=self.selected_factor_name,
            dropna=False,
        )

        if self.split_mode != SplitMode.TOTAL and self.split_mode != SplitMode.RUN:
            df[x] = df[x].cat.remove_unused_categories()

        self.canvas.clear(False)
        ax = self.canvas.figure.add_subplot(111)
        ax.tick_params(axis="x", rotation=90)

        if self.plot_type_combobox.currentText() == "Violin plot":
            sns.violinplot(data=df, x=x, y=variable.name, ax=ax)
        else:
            sns.boxplot(data=df, x=x, y=variable.name, gap=0.1, ax=ax)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self):
        self.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
