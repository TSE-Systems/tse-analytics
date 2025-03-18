import pandas as pd
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QAbstractItemView, QWidget, QVBoxLayout, QToolBar, QAbstractScrollArea
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget, get_widget_tool_button
from tse_analytics.core.toaster import make_toast
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.split_mode_selector import SplitModeSelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


class MatrixPlotWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Matrix Plot"

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

        self.variables_table_widget = VariablesTableWidget()
        self.variables_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.variables_table_widget.set_data(self.datatable.variables)
        self.variables_table_widget.setMaximumHeight(400)
        self.variables_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        variables_button = get_widget_tool_button(
            toolbar,
            self.variables_table_widget,
            "Variables",
            QIcon(":/icons/variables.png"),
        )
        toolbar.addWidget(variables_button)

        split_mode_selector = SplitModeSelector(toolbar, self.datatable.dataset.factors, self._split_mode_callback)
        toolbar.addWidget(split_mode_selector)

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self.layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

        self.toast = None

    def _split_mode_callback(self, mode: SplitMode, factor_name: str | None):
        self.split_mode = mode
        self.selected_factor_name = factor_name

    def _update(self):
        selected_variables = self.variables_table_widget.get_selected_variables_dict()
        if len(selected_variables) < 2:
            make_toast(
                self,
                self.title,
                "Please select at least two variables.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        if self.split_mode == SplitMode.FACTOR and self.selected_factor_name == "":
            make_toast(
                self,
                self.title,
                "Please select factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        df = self.datatable.get_preprocessed_df(
            variables=selected_variables,
            split_mode=self.split_mode,
            selected_factor_name=self.selected_factor_name,
            dropna=True,
        )

        match self.split_mode:
            case SplitMode.ANIMAL:
                colors, _ = pd.factorize(df["Animal"])
            case SplitMode.RUN:
                colors = df["Run"]
            case SplitMode.FACTOR:
                colors, _ = pd.factorize(df[self.selected_factor_name])
            case _:  # Total
                colors = None

        self.canvas.clear(False)
        ax = self.canvas.figure.add_subplot(111)

        pd.plotting.scatter_matrix(
            frame=df[list(selected_variables)],
            diagonal="hist",
            c=colors,
            ax=ax,
        )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self):
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
