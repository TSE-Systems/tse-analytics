from dataclasses import dataclass

import seaborn.objects as so
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtWidgets import QInputDialog, QLabel, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import color_manager, manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode
from tse_analytics.core.data.report import Report
from tse_analytics.core.utils import get_h_spacer_widget, get_html_image_from_figure
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class FastBarPlotWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None


class FastBarPlotWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: FastBarPlotWidgetSettings = settings.value(self.__class__.__name__, FastBarPlotWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Fast Bar Plot"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        self.variableSelector.currentTextChanged.connect(self._variable_changed)
        toolbar.addWidget(self.variableSelector)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(
            toolbar,
            self.datatable,
            selected_mode=self._settings.group_by,
        )
        self.group_by_selector.currentTextChanged.connect(self._refresh_data)
        toolbar.addWidget(self.group_by_selector)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self._layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        self.add_report_action = toolbar.addAction("Add Report")
        self.add_report_action.triggered.connect(self._add_report)

        self._refresh_data()

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            FastBarPlotWidgetSettings(
                self.group_by_selector.currentText(),
                self.variableSelector.currentText(),
            ),
        )

    def _variable_changed(self, variable: str) -> None:
        self._refresh_data()

    def _refresh_data(self):
        # Clear the plot
        self.canvas.clear(True)

        grouping_settings = self.group_by_selector.get_grouping_settings()
        selected_variable = self.variableSelector.get_selected_variable()

        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [selected_variable.name]
        df = self.datatable.get_filtered_df(columns)

        match grouping_settings.mode:
            case GroupingMode.ANIMAL:
                by = "Animal"
                # Cleaning
                df[by] = df[by].cat.remove_unused_categories()
                palette = color_manager.get_animal_to_color_dict(self.datatable.dataset.animals)
            case GroupingMode.FACTOR:
                by = grouping_settings.factor_name
                palette = color_manager.get_level_to_color_dict(self.datatable.dataset.factors[by])

        # TODO: workaround for issue with nullable Float64
        df[selected_variable.name] = df[selected_variable.name].astype(float)

        (
            so
            .Plot(
                df,
                x=by,
                y=selected_variable.name,
                color=by,
            )
            .add(so.Bar(), so.Agg())
            .add(so.Range(), so.Est(errorbar="se"))
            .facet("LightCycle", wrap=3)
            .share(y=True)
            .scale(color=palette)
            .on(self.canvas.figure)
            .plot(True)
        )

        for ax in self.canvas.figure.axes:  # works across facets too
            ax.tick_params(axis="x", rotation=90)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self):
        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text=self.title,
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.datatable.dataset,
                    name,
                    get_html_image_from_figure(self.canvas.figure),
                )
            )
