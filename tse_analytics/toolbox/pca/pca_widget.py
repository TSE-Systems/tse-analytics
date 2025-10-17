from dataclasses import dataclass, field

import pandas as pd
import seaborn.objects as so
from PySide6.QtCore import QSize, Qt, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QAbstractItemView, QWidget, QVBoxLayout, QToolBar, QAbstractScrollArea, QLabel
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import messaging, color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_html_image, get_widget_tool_button, get_h_spacer_widget
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


@dataclass
class PcaWidgetSettings:
    group_by: str = "Animal"
    selected_variables: list[str] = field(default_factory=list)


class PcaWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: PcaWidgetSettings = settings.value(self.__class__.__name__, PcaWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "PCA"

        self.datatable = datatable
        self._toast = None

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        self.update_action = toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update")
        self.update_action.triggered.connect(self._update)
        toolbar.addSeparator()

        self.variables_table_widget = VariablesTableWidget()
        self.variables_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.variables_table_widget.set_data(self.datatable.variables, self._settings.selected_variables)
        self.variables_table_widget.setMaximumHeight(600)
        self.variables_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        variables_button = get_widget_tool_button(
            toolbar,
            self.variables_table_widget,
            "Variables",
            QIcon(":/icons/variables.png"),
        )
        toolbar.addWidget(variables_button)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(toolbar, self.datatable, selected_mode=self._settings.group_by)
        toolbar.addWidget(self.group_by_selector)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.canvas = MplCanvas(self)
        self._layout.addWidget(self.canvas)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        self.add_report_action = toolbar.addAction("Add to Report")
        self.add_report_action.triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            PcaWidgetSettings(
                self.group_by_selector.currentText(),
                self.variables_table_widget.get_selected_variable_names(),
            ),
        )

    def _update(self):
        self.update_action.setEnabled(False)
        self.add_report_action.setEnabled(False)

        selected_variables = self.variables_table_widget.get_selected_variables_dict()
        if len(selected_variables) < 3:
            make_toast(
                self,
                self.title,
                "Please select at least three variables.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        split_mode, selected_factor_name = self.group_by_selector.get_group_by()

        match split_mode:
            case SplitMode.ANIMAL:
                by = "Animal"
            case SplitMode.RUN:
                by = "Run"
            case SplitMode.FACTOR:
                by = selected_factor_name
            case _:
                by = None

        self._toast = make_toast(self, self.title, "Processing...")
        self._toast.show()

        worker = Worker(self._calculate, selected_variables, split_mode, selected_factor_name, by)
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _calculate(
        self,
        selected_variables: dict[str, Variable],
        split_mode: SplitMode,
        selected_factor_name: str,
        by: str,
    ) -> tuple[pd.DataFrame, str, str, SplitMode, str]:
        selected_variable_names = list(selected_variables)

        df = self.datatable.get_df(
            selected_variable_names,
            split_mode,
            selected_factor_name,
        )
        df.dropna(inplace=True)

        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df[selected_variable_names])

        pca = PCA(n_components=2)
        data = pca.fit_transform(scaled_data)
        total_var = pca.explained_variance_ratio_.sum() * 100
        title = f"PCA. Total Explained Variance: {total_var:.2f}%"

        result_df = pd.DataFrame(data=data, columns=["PC1", "PC2"])
        if by is not None:
            result_df = pd.concat([result_df, df[[by]]], axis=1)

        return result_df, title, by, split_mode, selected_factor_name

    def _result(self, result: tuple[pd.DataFrame, str, str, SplitMode, str]):
        # Clear the plot
        self.canvas.clear(False)

        df, title, by, split_mode, selected_factor_name = result

        match split_mode:
            case SplitMode.ANIMAL:
                palette = color_manager.get_animal_to_color_dict(self.datatable.dataset.animals)
            case SplitMode.RUN:
                palette = color_manager.colormap_name
            case SplitMode.FACTOR:
                palette = color_manager.get_level_to_color_dict(self.datatable.dataset.factors[selected_factor_name])
            case _:
                palette = color_manager.colormap_name

        (
            so.Plot(
                df,
                x="PC1",
                y="PC2",
                color=by,
            )
            .add(so.Dot(pointsize=3))
            .scale(color=palette)
            .label(title=title)
            .on(self.canvas.figure)
            .plot(True)
        )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _finished(self):
        self._toast.hide()
        self.update_action.setEnabled(True)
        self.add_report_action.setEnabled(True)

    def _add_report(self):
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
