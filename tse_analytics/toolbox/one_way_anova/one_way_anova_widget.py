from dataclasses import dataclass

from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QInputDialog, QLabel, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_figsize_from_widget, get_h_spacer_widget
from tse_analytics.pipeline.enums import EFFECT_SIZE
from tse_analytics.toolbox.one_way_anova.processor import get_one_way_anova_result
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.report_edit import ReportEdit
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class OneWayAnovaWidgetSettings:
    selected_variable: str = None
    selected_factor: str = None


class OneWayAnovaWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: OneWayAnovaWidgetSettings = settings.value(self.__class__.__name__, OneWayAnovaWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "One-way ANOVA"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("Dependent variable:"))
        self.variable_selector = VariableSelector(toolbar)
        self.variable_selector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variable_selector)

        toolbar.addWidget(QLabel("Factor:"))
        self.factor_selector = FactorSelector(toolbar)
        self.factor_selector.set_data(self.datatable.dataset.factors, selected_factor=self._settings.selected_factor)
        toolbar.addWidget(self.factor_selector)

        toolbar.addWidget(QLabel("Effect size type:"))
        self.comboBoxEffectSizeType = QComboBox(toolbar)
        self.comboBoxEffectSizeType.addItems(list(EFFECT_SIZE))
        self.comboBoxEffectSizeType.setCurrentText("Hedges g")
        toolbar.addWidget(self.comboBoxEffectSizeType)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.report_view = ReportEdit(self)
        self._layout.addWidget(self.report_view)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add Report").triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            OneWayAnovaWidgetSettings(
                self.variable_selector.currentText(),
                self.factor_selector.currentText(),
            ),
        )

    def _update(self):
        self.report_view.clear()

        dependent_variable = self.variable_selector.get_selected_variable()
        if dependent_variable is None:
            make_toast(
                self,
                self.title,
                "Please select dependent variable.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        factor_name = self.factor_selector.currentText()
        if factor_name == "":
            make_toast(
                self,
                self.title,
                "Please select a single factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        columns = (
            self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + [dependent_variable.name]
        )
        df = self.datatable.get_filtered_df(columns)

        result = get_one_way_anova_result(
            self.datatable.dataset,
            df,
            dependent_variable,
            factor_name,
            EFFECT_SIZE[self.comboBoxEffectSizeType.currentText()],
            get_figsize_from_widget(self.report_view),
        )

        self.report_view.set_content(result.report)

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
                    self.report_view.toHtml(),
                )
            )
