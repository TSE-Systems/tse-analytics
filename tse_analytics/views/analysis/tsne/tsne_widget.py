import pandas as pd
import seaborn as sns
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QAbstractItemView, QWidget, QVBoxLayout, QToolBar, QAbstractScrollArea
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

from tse_analytics.core import messaging, color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.utils import get_html_image, get_widget_tool_button, get_h_spacer_widget
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.workers.task_manager import TaskManager
from tse_analytics.core.workers.worker import Worker
from tse_analytics.views.misc.MplCanvas import MplCanvas
from tse_analytics.views.misc.split_mode_selector import SplitModeSelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


class TsneWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "tSNE"

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

        self.toast = None

    def _split_mode_callback(self, mode: SplitMode, factor_name: str | None):
        self.split_mode = mode
        self.selected_factor_name = factor_name

    def _update(self):
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

        match self.split_mode:
            case SplitMode.ANIMAL:
                by = "Animal"
            case SplitMode.RUN:
                by = "Run"
            case SplitMode.FACTOR:
                by = self.selected_factor_name
            case _:
                by = None

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

        # self.ui.pushButtonUpdate.setEnabled(False)
        # self.ui.pushButtonAddReport.setEnabled(False)

        self.toast = make_toast(self, self.title, "Processing...")
        self.toast.show()

        worker = Worker(self._calculate, selected_variables, self.split_mode, self.selected_factor_name, by)
        worker.signals.result.connect(self._result)
        worker.signals.finished.connect(self._finished)
        TaskManager.start_task(worker)

    def _calculate(
        self,
        selected_variables: dict[str, Variable],
        split_mode: SplitMode,
        selected_factor_name: str,
        by: str,
    ) -> tuple[pd.DataFrame, str, str]:
        df = self.datatable.get_preprocessed_df(
            variables=selected_variables,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            dropna=True,
        )

        selected_variable_names = list(selected_variables)

        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df[selected_variable_names])

        tsne = TSNE(n_components=2, random_state=0)
        data = tsne.fit_transform(scaled_data)
        title = "tSNE"

        result_df = pd.DataFrame(data=data, columns=["tSNE1", "tSNE2"])
        if by is not None:
            result_df = pd.concat([result_df, df[[by]]], axis=1)

        return result_df, title, by

    def _result(self, result: tuple):
        self.canvas.clear(False)
        ax = self.canvas.figure.add_subplot(111)

        df, title, by = result

        match self.split_mode:
            case SplitMode.ANIMAL:
                palette = color_manager.get_animal_to_color_dict(self.datatable.dataset.animals)
            case SplitMode.RUN:
                palette = color_manager.colormap_name
            case SplitMode.FACTOR:
                palette = color_manager.get_level_to_color_dict(
                    self.datatable.dataset.factors[self.selected_factor_name]
                )
            case _:
                palette = color_manager.colormap_name

        sns.scatterplot(
            data=df,
            x="tSNE1",
            y="tSNE2",
            hue=by,
            marker=".",
            palette=palette,
            ax=ax,
        )
        ax.set_title(title)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _finished(self):
        self.toast.hide()
        # self.ui.pushButtonUpdate.setEnabled(True)
        # self.ui.pushButtonAddReport.setEnabled(True)

    def _add_report(self):
        self.datatable.dataset.report += get_html_image(self.canvas.figure)
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
