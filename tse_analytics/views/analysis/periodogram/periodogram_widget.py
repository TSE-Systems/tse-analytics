import numpy as np
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from scipy.signal import lombscargle

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.core.toaster import make_toast
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.split_mode_selector import SplitModeSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class PeriodogramWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Periodogram"

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

        variable = self.variableSelector.get_selected_variable()

        match self.split_mode:
            case SplitMode.ANIMAL:
                by = "Animal"
            case SplitMode.RUN:
                by = "Run"
            case SplitMode.FACTOR:
                by = self.selected_factor_name
            case _:
                by = None

        df = self.datatable.get_preprocessed_df(
            variables={variable.name: variable},
            split_mode=self.split_mode,
            selected_factor_name=self.selected_factor_name,
            dropna=False,
        )

        number_of_elements = 1
        if self.split_mode != SplitMode.TOTAL and self.split_mode != SplitMode.RUN:
            df[by] = df[by].cat.remove_unused_categories()
            number_of_elements = len(df[by].cat.categories)
        elif self.split_mode == SplitMode.RUN:
            number_of_elements = df[by].nunique()

        self.canvas.clear(False)
        axes = self.canvas.figure.subplots(4, 1)

        x = df["DateTime"]
        y = df[variable.name]

        nout = 1002
        w = np.linspace(0.25, 10, nout)

        pgram_power = lombscargle(x, y, w, normalize=False)
        pgram_norm = lombscargle(x, y, w, normalize=True)
        pgram_amp = lombscargle(x, y, w, normalize="amplitude")
        pgram_power_f = lombscargle(x, y, w, normalize=False, floating_mean=True)
        pgram_norm_f = lombscargle(x, y, w, normalize=True, floating_mean=True)
        pgram_amp_f = lombscargle(x, y, w, normalize="amplitude", floating_mean=True)

        axes[0].plot(x, y)
        axes[0].set_xlabel("Time [s]")
        axes[0].set_ylabel("Amplitude")

        axes[1].plot(w, pgram_power, label="default")
        axes[1].plot(w, pgram_power_f, label="floating_mean=True")
        axes[1].set_xlabel("Angular frequency [rad/s]")
        axes[1].set_ylabel("Power")
        axes[1].legend(prop={"size": 7})

        axes[2].plot(w, pgram_norm, label="default")
        axes[2].plot(w, pgram_norm_f, label="floating_mean=True")
        axes[2].set_xlabel("Angular frequency [rad/s]")
        axes[2].set_ylabel("Normalized")
        axes[2].legend(prop={"size": 7})

        axes[3].plot(w, np.abs(pgram_amp), label="default")
        axes[3].plot(w, np.abs(pgram_amp_f), label="floating_mean=True")
        axes[3].set_xlabel("Angular frequency [rad/s]")
        axes[3].set_ylabel("Amplitude")
        axes[3].legend(prop={"size": 7})

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self) -> None:
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
