from dataclasses import dataclass

import pingouin as pg
from PySide6.QtCore import QSize, Qt, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QToolBar, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt import NavigationToolbar2QT

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class NormalityWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None


class NormalityWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: NormalityWidgetSettings = settings.value(self.__class__.__name__, NormalityWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Normality"

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
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self._layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            NormalityWidgetSettings(
                self.group_by_selector.currentText(),
                self.variableSelector.currentText(),
            ),
        )

    def _update(self):
        # Clear the plot
        self.canvas.clear(False)

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
        # df.dropna(inplace=True)

        if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
            df[by] = df[by].cat.remove_unused_categories()

        match split_mode:
            case SplitMode.ANIMAL:
                animals = df["Animal"].unique()
                nrows, ncols = self._get_plot_layout(len(animals))
                for index, animal in enumerate(animals):
                    ax = self.canvas.figure.add_subplot(nrows, ncols, index + 1)
                    pg.qqplot(
                        df[df["Animal"] == animal][variable.name],
                        dist="norm",
                        marker=".",
                        ax=ax,
                    )
                    ax.set_title(f"Animal: {animal}")
            case SplitMode.FACTOR:
                levels = df[selected_factor_name].unique()
                nrows, ncols = self._get_plot_layout(len(levels))
                for index, level in enumerate(levels):
                    # TODO: NaN check
                    if level != level:
                        continue
                    ax = self.canvas.figure.add_subplot(nrows, ncols, index + 1)
                    pg.qqplot(
                        df[df[selected_factor_name] == level][variable.name],
                        dist="norm",
                        marker=".",
                        ax=ax,
                    )
                    ax.set_title(level)
            case SplitMode.RUN:
                runs = df["Run"].unique()
                nrows, ncols = self._get_plot_layout(len(runs))
                for index, run in enumerate(runs):
                    ax = self.canvas.figure.add_subplot(nrows, ncols, index + 1)
                    pg.qqplot(
                        df[df["Run"] == run][variable.name],
                        dist="norm",
                        marker=".",
                        ax=ax,
                    )
                    ax.set_title(f"Run: {run}")
            case SplitMode.TOTAL:
                ax = self.canvas.figure.add_subplot(1, 1, 1)
                pg.qqplot(
                    df[variable.name],
                    dist="norm",
                    marker=".",
                    ax=ax,
                )
                ax.set_title("Total")

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

    def _add_report(self):
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
