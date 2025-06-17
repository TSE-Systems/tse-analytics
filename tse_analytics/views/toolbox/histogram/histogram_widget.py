from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel
from matplotlib.backends.backend_qt import NavigationToolbar2QT

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class HistogramWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Histogram"

        self.datatable = datatable

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

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, check_binning=False)
        toolbar.addWidget(self.group_by_selector)

        # toolbar.addSeparator()
        # self.log_scale_checkbox = QCheckBox("Log Scale")
        # toolbar.addWidget(self.log_scale_checkbox)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self.layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

    def _update(self):
        split_mode, selected_factor_name = self.group_by_selector.get_group_by()
        variable = self.variableSelector.get_selected_variable()

        match split_mode:
            case SplitMode.ANIMAL:
                by = "Animal"
            case SplitMode.RUN:
                by = "Run"
            case SplitMode.FACTOR:
                by = selected_factor_name
            case _:
                by = None

        df = self.datatable.get_df(
            [variable.name],
            split_mode,
            selected_factor_name,
        )

        number_of_elements = 1
        if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
            df[by] = df[by].cat.remove_unused_categories()
            number_of_elements = len(df[by].cat.categories)
        elif split_mode == SplitMode.RUN:
            number_of_elements = df[by].nunique()

        self.canvas.clear(False)
        ax = self.canvas.figure.add_subplot(111)

        # Use non-equal bin sizes, such that they look equal on a log scale.
        # nbins = 20
        # bins = (
        #     np.geomspace(df[variable.name].min(), df[variable.name].max(), nbins + 1)
        #     if self.log_scale_checkbox.isChecked()
        #     else nbins
        # )

        df.plot(
            kind="hist",
            column=[variable.name],
            by=by,
            bins=20,
            sharex=False,
            sharey=False,
            # logx=self.log_scale_checkbox.isChecked(),
            layout=self._get_plot_layout(number_of_elements),
            ax=ax,
        )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _get_plot_layout(self, number_of_elements: int):
        if number_of_elements == 1:
            return 1, 1
        elif number_of_elements == 2:
            return 1, 2
        elif number_of_elements <= 4:
            return 2, 2
        else:
            return round(number_of_elements / 3) + 1, 3

    def _add_report(self) -> None:
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
