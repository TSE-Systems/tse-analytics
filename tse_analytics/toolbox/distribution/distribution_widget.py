from dataclasses import dataclass

import seaborn as sns
from PySide6.QtCore import QSize, Qt, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QComboBox, QLabel, QCheckBox
from matplotlib.backends.backend_qt import NavigationToolbar2QT

from tse_analytics.core import messaging, color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class DistributionWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None
    show_points: bool = False
    plot_type: str = "Violin plot"


class DistributionWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: DistributionWidgetSettings = settings.value(
            self.__class__.__name__, DistributionWidgetSettings()
        )

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Distribution"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
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

        self.plot_type_combobox = QComboBox(toolbar)
        self.plot_type_combobox.addItems(["Violin plot", "Box plot"])
        self.plot_type_combobox.setCurrentText(self._settings.plot_type)
        toolbar.addWidget(self.plot_type_combobox)

        self.checkBoxShowPoints = QCheckBox("Show Points", toolbar)
        self.checkBoxShowPoints.setChecked(self._settings.show_points)
        toolbar.addWidget(self.checkBoxShowPoints)

        # Insert toolbar to the widget
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
            DistributionWidgetSettings(
                self.group_by_selector.currentText(),
                self.variableSelector.currentText(),
                self.checkBoxShowPoints.isChecked(),
                self.plot_type_combobox.currentText(),
            ),
        )

    def _update(self):
        # Clear the plot
        self.canvas.clear(False)

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()
        variable = self.variableSelector.get_selected_variable()

        match split_mode:
            case SplitMode.ANIMAL:
                x = "Animal"
                palette = color_manager.get_animal_to_color_dict(self.datatable.dataset.animals)
            case SplitMode.RUN:
                x = "Run"
                palette = color_manager.colormap_name
            case SplitMode.FACTOR:
                x = selected_factor_name
                palette = color_manager.get_level_to_color_dict(self.datatable.dataset.factors[selected_factor_name])
            case _:
                x = None
                palette = color_manager.colormap_name

        df = self.datatable.get_df(
            [variable.name],
            split_mode,
            selected_factor_name,
        )

        if split_mode != SplitMode.TOTAL and split_mode != SplitMode.RUN:
            df[x] = df[x].cat.remove_unused_categories()

        ax = self.canvas.figure.add_subplot(1, 1, 1)
        ax.tick_params(axis="x", rotation=90)

        if self.plot_type_combobox.currentText() == "Violin plot":
            sns.violinplot(
                data=df,
                x=x,
                y=variable.name,
                hue=x,
                palette=palette,
                inner="quartile" if self.checkBoxShowPoints.isChecked() else "box",
                saturation=1,
                fill=not self.checkBoxShowPoints.isChecked(),
                legend=False,
                ax=ax,
            )
        else:
            sns.boxplot(
                data=df,
                x=x,
                y=variable.name,
                hue=x,
                palette=palette,
                saturation=1,
                fill=not self.checkBoxShowPoints.isChecked(),
                legend=False,
                gap=0.1,
                ax=ax,
            )

        if self.checkBoxShowPoints.isChecked():
            sns.stripplot(
                data=df,
                x=x,
                y=variable.name,
                hue=x,
                palette=palette,
                legend=False,
                marker=".",
                ax=ax,
            )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _add_report(self):
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
