import pingouin as pg
from pyqttoast import ToastPreset
from PySide6.QtWidgets import QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.helper import show_help
from tse_analytics.core.toaster import make_toast
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.analysis.ancova.ancova_widget_ui import Ui_AncovaWidget


class AncovaWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_AncovaWidget()
        self.ui.setupUi(self)

        self.title = "ANCOVA"
        self.help_path = "ANCOVA.md"

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        self.p_adjustment = {
            "No correction": "none",
            "One-step Bonferroni": "bonf",
            "One-step Sidak": "sidak",
            "Step-down Bonferroni": "holm",
            "Benjamini/Hochberg FDR": "fdr_bh",
            "Benjamini/Yekutieli FDR": "fdr_by",
        }
        self.ui.comboBoxPAdjustment.addItems(self.p_adjustment.keys())
        self.ui.comboBoxPAdjustment.setCurrentText("No correction")

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
        self.ui.comboBoxEffectSizeType.addItems(self.eff_size.keys())
        self.ui.comboBoxEffectSizeType.setCurrentText("Hedges g")

        self.ui.textEdit.document().setDefaultStyleSheet(style_descriptive_table)

        self.dataset = dataset
        self.ui.tableWidgetFactors.set_data(self.dataset.factors)
        self.ui.tableWidgetDependentVariable.set_data(self.dataset.variables)
        self.ui.tableWidgetCovariates.set_data(self.dataset.variables)

    def _update(self):
        selected_dependent_variables = self.ui.tableWidgetDependentVariable.get_selected_variables_dict()
        if len(selected_dependent_variables) == 0:
            make_toast(
                self,
                self.title,
                "Please select dependent variable.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        selected_factor_names = self.ui.tableWidgetFactors.get_selected_factor_names()
        if len(selected_factor_names) != 1:
            make_toast(
                self,
                self.title,
                "Please select a single factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        factor_name = selected_factor_names[0]

        dependent_variable = next(iter(selected_dependent_variables.values())).name

        selected_covariate_variables = self.ui.tableWidgetCovariates.get_selected_variables_dict()
        selected_covariates = list(selected_covariate_variables)

        variables = selected_dependent_variables | selected_covariate_variables

        df = self.dataset.get_anova_df(variables=variables)

        padjust = self.p_adjustment[self.ui.comboBoxPAdjustment.currentText()]
        effsize = self.eff_size[self.ui.comboBoxEffectSizeType.currentText()]

        ancova = pg.ancova(
            data=df,
            dv=dependent_variable,
            covar=selected_covariates,
            between=factor_name,
        ).round(5)

        pairwise_tests = pg.pairwise_tests(
            data=df,
            dv=dependent_variable,
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
        self.ui.textEdit.document().setHtml(html)

    def _add_report(self):
        self.dataset.report += self.ui.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
