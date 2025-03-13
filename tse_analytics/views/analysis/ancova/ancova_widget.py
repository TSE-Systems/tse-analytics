import pingouin as pg
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QTextEdit, QAbstractItemView, QAbstractScrollArea
from pyqttoast import ToastPreset

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.utils import get_widget_tool_button, get_h_spacer_widget
from tse_analytics.core.toaster import make_toast
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.analysis.ancova.ancova_settings_widget_ui import Ui_AncovaSettingsWidget
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_analytics.views.misc.variables_table_widget import VariablesTableWidget


class AncovaWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = "ANCOVA"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Data Plot Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("Dependent variable:"))
        self.variable_selector = VariableSelector(toolbar)
        self.variable_selector.set_data(self.datatable.variables)
        toolbar.addWidget(self.variable_selector)

        self.covariates_table_widget = VariablesTableWidget()
        self.covariates_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.covariates_table_widget.set_data(self.datatable.variables)
        self.covariates_table_widget.setMaximumHeight(400)
        self.covariates_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        covariates_button = get_widget_tool_button(
            toolbar,
            self.covariates_table_widget,
            "Covariates",
            QIcon(":/icons/variables.png"),
        )
        toolbar.addWidget(covariates_button)

        toolbar.addWidget(QLabel("Factor:"))
        self.factor_selector = FactorSelector(toolbar)
        self.factor_selector.set_data(self.datatable.dataset.factors, add_empty_item=False)
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

        self.p_adjustment = {
            "No correction": "none",
            "One-step Bonferroni": "bonf",
            "One-step Sidak": "sidak",
            "Step-down Bonferroni": "holm",
            "Benjamini/Hochberg FDR": "fdr_bh",
            "Benjamini/Yekutieli FDR": "fdr_by",
        }
        self.settings_widget_ui.comboBoxPAdjustment.addItems(self.p_adjustment.keys())
        self.settings_widget_ui.comboBoxPAdjustment.setCurrentText("No correction")

        self.eff_size = {
            "No effect size": "none",
            "Unbiased Cohen d": "cohen",
            "Hedges g": "hedges",
            # "Pearson correlation coefficient": "r",
            "Eta-square": "eta-square",
            "Odds ratio": "odds-ratio",
            "Area Under the Curve": "AUC",
            "Common Language Effect Size": "CLES",
        }
        self.settings_widget_ui.comboBoxEffectSizeType.addItems(self.eff_size.keys())
        self.settings_widget_ui.comboBoxEffectSizeType.setCurrentText("Hedges g")

        # Insert toolbar to the widget
        self.layout.addWidget(toolbar)

        self.textEdit = QTextEdit(
            toolbar,
            undoRedoEnabled=False,
            readOnly=True,
            lineWrapMode=QTextEdit.LineWrapMode.NoWrap,
        )
        self.textEdit.document().setDefaultStyleSheet(style_descriptive_table)
        self.layout.addWidget(self.textEdit)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

    def _update(self):
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

        dependent_variable_name = dependent_variable.name

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

        selected_covariate_variables = self.covariates_table_widget.get_selected_variables_dict()
        selected_covariates = list(selected_covariate_variables)

        variables = {dependent_variable_name: dependent_variable} | selected_covariate_variables

        df = self.datatable.get_anova_df(variables=variables)

        padjust = self.p_adjustment[self.settings_widget_ui.comboBoxPAdjustment.currentText()]
        effsize = self.eff_size[self.settings_widget_ui.comboBoxEffectSizeType.currentText()]

        ancova = pg.ancova(
            data=df,
            dv=dependent_variable_name,
            covar=selected_covariates,
            between=factor_name,
        ).round(5)

        pairwise_tests = pg.pairwise_tests(
            data=df,
            dv=dependent_variable_name,
            between=factor_name,
            effsize=effsize,
            padjust=padjust,
            return_desc=True,
        ).round(5)

        html_template = """
                        <h1>Factor: {factor_name}</h1>
                        <h2>ANCOVA</h2>
                        {ancova}
                        <h2>Pairwise post-hoc tests</h2>
                        {pairwise_tests}
                        """

        html = html_template.format(
            factor_name=factor_name,
            ancova=ancova.to_html(),
            pairwise_tests=pairwise_tests.to_html(),
        )
        self.textEdit.document().setHtml(html)

    def _add_report(self):
        self.datatable.dataset.report += self.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
