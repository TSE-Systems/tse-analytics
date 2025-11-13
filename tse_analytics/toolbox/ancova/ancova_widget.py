from dataclasses import dataclass

import pingouin as pg
from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QTextEdit, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_h_spacer_widget, get_html_table, get_widget_tool_button
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.toolbox.ancova.ancova_settings_widget_ui import Ui_AncovaSettingsWidget
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class AncovaWidgetSettings:
    selected_variable: str = None
    selected_covariate: str = None
    selected_factor: str = None


class AncovaWidget(QWidget):
    p_adjustment = {
        "No correction": "none",
        "One-step Bonferroni": "bonf",
        "One-step Sidak": "sidak",
        "Step-down Bonferroni": "holm",
        "Benjamini/Hochberg FDR": "fdr_bh",
        "Benjamini/Yekutieli FDR": "fdr_by",
    }

    eff_size = {
        "No effect size": "none",
        "Unbiased Cohen d": "cohen",
        "Hedges g": "hedges",
        # "Pearson correlation coefficient": "r",
        "Eta-square": "eta-square",
        "Odds ratio": "odds-ratio",
        "Area Under the Curve": "AUC",
        "Common Language Effect Size": "CLES",
    }

    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: AncovaWidgetSettings = settings.value(self.__class__.__name__, AncovaWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "ANCOVA"

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

        toolbar.addWidget(QLabel("Covariate variable:"))
        self.covariate_selector = VariableSelector(toolbar)
        self.covariate_selector.set_data(self.datatable.variables, selected_variable=self._settings.selected_covariate)
        toolbar.addWidget(self.covariate_selector)

        toolbar.addWidget(QLabel("Factor:"))
        self.factor_selector = FactorSelector(toolbar)
        self.factor_selector.set_data(self.datatable.dataset.factors, selected_factor=self._settings.selected_factor)
        toolbar.addWidget(self.factor_selector)

        self.settings_widget = QWidget()
        self.settings_widget_ui = Ui_AncovaSettingsWidget()
        self.settings_widget_ui.setupUi(self.settings_widget)
        settings_button = get_widget_tool_button(
            toolbar,
            self.settings_widget,
            "Settings",
            QIcon(":/icons/icons8-settings-16.png"),
        )
        toolbar.addWidget(settings_button)

        self.settings_widget_ui.comboBoxPAdjustment.addItems(self.p_adjustment.keys())
        self.settings_widget_ui.comboBoxPAdjustment.setCurrentText("No correction")

        self.settings_widget_ui.comboBoxEffectSizeType.addItems(self.eff_size.keys())
        self.settings_widget_ui.comboBoxEffectSizeType.setCurrentText("Hedges g")

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.textEdit = QTextEdit(
            toolbar,
            undoRedoEnabled=False,
            readOnly=True,
            lineWrapMode=QTextEdit.LineWrapMode.NoWrap,
        )
        self.textEdit.document().setDefaultStyleSheet(style_descriptive_table)
        self._layout.addWidget(self.textEdit)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            AncovaWidgetSettings(
                self.variable_selector.currentText(),
                self.covariate_selector.currentText(),
                self.factor_selector.currentText(),
            ),
        )

    def _update(self):
        dependent_variable = self.variable_selector.get_selected_variable()
        selected_covariate = self.covariate_selector.get_selected_variable()

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

        variables = {
            dependent_variable.name: dependent_variable,
            selected_covariate.name: selected_covariate,
        }

        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + list(variables)
        df = self.datatable.get_filtered_df(columns)

        # Binning
        df = process_time_interval_binning(
            df,
            TimeIntervalsBinningSettings("day", 365),
            variables,
            origin=self.datatable.dataset.experiment_started,
        )

        # TODO: should or should not?
        df.dropna(inplace=True)

        padjust = self.p_adjustment[self.settings_widget_ui.comboBoxPAdjustment.currentText()]
        effsize = self.eff_size[self.settings_widget_ui.comboBoxEffectSizeType.currentText()]

        ancova = pg.ancova(
            data=df,
            dv=dependent_variable.name,
            covar=selected_covariate.name,
            between=factor_name,
        )

        pairwise_tests = pg.pairwise_tests(
            data=df,
            dv=dependent_variable.name,
            between=factor_name,
            effsize=effsize,
            padjust=padjust,
            return_desc=True,
        )

        html_template = """
                        {ancova}
                        {pairwise_tests}
                        """

        html = html_template.format(
            ancova=get_html_table(ancova, "ANCOVA", index=False),
            pairwise_tests=get_html_table(pairwise_tests, "Pairwise post-hoc tests", index=False),
        )
        self.textEdit.document().setHtml(html)

    def _add_report(self):
        self.datatable.dataset.report += self.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
