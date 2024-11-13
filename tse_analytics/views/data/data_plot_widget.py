from matplotlib.backends.backend_qt import NavigationToolbar2QT
from pyqttoast import ToastPreset
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.manager import Manager
from tse_analytics.core.toaster import make_toast
from tse_analytics.views.data.bar_plot_view import BarPlotView
from tse_analytics.views.data.data_plot_widget_ui import Ui_DataPlotWidget
from tse_analytics.views.data.timeline_plot_view import TimelinePlotView


class DataPlotWidget(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_DataPlotWidget()
        self.ui.setupUi(self)

        messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)
        messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
        messaging.subscribe(self, messaging.DataChangedMessage, self._on_data_changed)

        self.ui.radioButtonSplitTotal.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByAnimal.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByFactor.toggled.connect(self._split_mode_toggled)
        self.ui.radioButtonSplitByRun.toggled.connect(self._split_mode_toggled)

        self.ui.variableSelector.currentTextChanged.connect(self._variable_changed)
        self.ui.factorSelector.currentTextChanged.connect(self._factor_changed)
        self.ui.checkBoxScatterPlot.stateChanged.connect(self._set_scatter_plot)
        self.ui.groupBoxDisplayErrors.toggled.connect(self._display_errors_toggled)
        self.ui.radioButtonStandardDeviation.toggled.connect(self._error_type_std_toggled)
        self.ui.radioButtonStandardError.toggled.connect(self._error_type_ste_toggled)

        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        self.timelinePlotView = TimelinePlotView(self)
        self.barPlotView = BarPlotView(self)

        self.ui.splitter.replaceWidget(0, self.timelinePlotView)

        self.plot_toolbar = NavigationToolbar2QT(self.barPlotView.canvas, self)
        self.plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().addWidget(self.plot_toolbar)
        self.plot_toolbar.hide()

    def _get_split_mode(self) -> SplitMode:
        if self.ui.radioButtonSplitByAnimal.isChecked():
            return SplitMode.ANIMAL
        elif self.ui.radioButtonSplitByRun.isChecked():
            return SplitMode.RUN
        elif self.ui.radioButtonSplitByFactor.isChecked():
            return SplitMode.FACTOR
        else:
            return SplitMode.TOTAL

    def _variable_changed(self, variable: str) -> None:
        self._refresh_data()

    def _factor_changed(self, factor_name: str) -> None:
        self._refresh_data()

    def _error_type_std_toggled(self, toggled: bool) -> None:
        if not toggled:
            return
        self._refresh_data()

    def _error_type_ste_toggled(self, toggled: bool) -> None:
        if not toggled:
            return
        self._refresh_data()

    def _display_errors_toggled(self, toggled: bool) -> None:
        self._refresh_data()

    def _set_scatter_plot(self, state: bool):
        self._refresh_data()

    def _on_dataset_changed(self, message: messaging.DatasetChangedMessage):
        self.ui.pushButtonAddReport.setDisabled(message.dataset is None)
        if message.dataset is None:
            self.ui.variableSelector.clear()
            self.ui.factorSelector.clear()
            self.timelinePlotView.clear_plot()
            self.barPlotView.clear_plot()
        else:
            self.ui.variableSelector.set_data(message.dataset.variables)
            self.ui.factorSelector.set_data(message.dataset.factors, add_empty_item=False)
            self._refresh_data()

    def _on_binning_applied(self, message: messaging.BinningMessage):
        self._refresh_data()

    def _on_data_changed(self, message: messaging.DataChangedMessage):
        self._refresh_data()

    def _split_mode_toggled(self, toggled: bool):
        if not toggled:
            return
        self.ui.factorSelector.setEnabled(self.ui.radioButtonSplitByFactor.isChecked())
        self._refresh_data()

    def _refresh_data(self):
        if Manager.data.selected_dataset is None:
            return

        selected_factor_name = self.ui.factorSelector.currentText()
        split_mode = self._get_split_mode()

        if split_mode == SplitMode.FACTOR and selected_factor_name == "":
            make_toast(
                self,
                "Data Plot",
                "Please select factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        selected_variable = self.ui.variableSelector.get_selected_variable()
        display_errors = self.ui.groupBoxDisplayErrors.isChecked()

        if not Manager.data.selected_dataset.binning_settings.apply:
            self._display_timeline_plot(selected_variable, split_mode, selected_factor_name, display_errors)
        else:
            if Manager.data.selected_dataset.binning_settings.mode == BinningMode.INTERVALS:
                self._display_timeline_plot(selected_variable, split_mode, selected_factor_name, display_errors)
            else:
                self._display_bar_plot(selected_variable, split_mode, selected_factor_name, display_errors)

    def _display_timeline_plot(
        self,
        selected_variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
        display_errors: bool,
    ):
        self.ui.splitter.replaceWidget(0, self.timelinePlotView)
        self.barPlotView.hide()
        self.timelinePlotView.show()
        self.plot_toolbar.hide()
        self.ui.checkBoxScatterPlot.show()

        if display_errors:
            calculate_errors = "sem" if self.ui.radioButtonStandardError.isChecked() else "std"
        else:
            calculate_errors = None

        df = Manager.data.get_timeline_plot_df(
            variable=selected_variable,
            split_mode=split_mode,
            selected_factor_name=selected_factor_name,
            calculate_errors=calculate_errors,
        )

        selected_factor = (
            Manager.data.selected_dataset.factors[selected_factor_name] if selected_factor_name != "" else None
        )

        if not df.empty:
            self.timelinePlotView.refresh_data(
                df,
                selected_variable,
                split_mode,
                display_errors,
                selected_factor,
                self.ui.checkBoxScatterPlot.isChecked(),
            )
        else:
            self.timelinePlotView.clear_plot()

    def _display_bar_plot(
        self,
        selected_variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
        display_errors: bool,
    ):
        self.ui.splitter.replaceWidget(0, self.barPlotView)
        self.timelinePlotView.hide()
        self.barPlotView.show()
        self.ui.checkBoxScatterPlot.hide()

        if display_errors:
            calculate_errors = "se" if self.ui.radioButtonStandardError.isChecked() else "sd"
        else:
            calculate_errors = None

        df = Manager.data.get_bar_plot_df(
            variable=selected_variable,
        )

        selected_factor = (
            Manager.data.selected_dataset.factors[selected_factor_name] if selected_factor_name != "" else None
        )

        self.barPlotView.refresh_data(
            df,
            selected_variable,
            split_mode,
            selected_factor,
            display_errors,
            calculate_errors,
        )

        new_toolbar = NavigationToolbar2QT(self.barPlotView.canvas, self)
        new_toolbar.setIconSize(QSize(16, 16))
        self.plot_toolbar.hide()
        self.ui.widgetSettings.layout().replaceWidget(self.plot_toolbar, new_toolbar)
        self.plot_toolbar.deleteLater()
        self.plot_toolbar = new_toolbar

    def _add_report(self):
        if not Manager.data.selected_dataset.binning_settings.apply:
            html = self.timelinePlotView.get_report()
        else:
            if Manager.data.selected_dataset.binning_settings.mode == BinningMode.INTERVALS:
                html = self.timelinePlotView.get_report()
            else:
                html = self.barPlotView.get_report()
        messaging.broadcast(messaging.AddToReportMessage(self, html))
