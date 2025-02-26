import pingouin as pg
from pyqttoast import ToastPreset
from PySide6.QtWidgets import QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.toaster import make_toast
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.analysis.n_way_anova.n_way_anova_widget_ui import Ui_NWayAnovaWidget


class NWayAnovaWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_NWayAnovaWidget()
        self.ui.setupUi(self)

        self.title = "N-way ANOVA"

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

        match len(selected_factor_names):
            case 2:
                anova_header = "Two-way ANOVA"
            case 3:
                anova_header = "Three-way ANOVA"
            case _:
                anova_header = "Multi-way ANOVA"

        if len(selected_factor_names) < 2:
            make_toast(
                self,
                anova_header,
                "Please select several factors.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        df = self.dataset.get_anova_df(variables=selected_dependent_variables)

        dependent_variable = next(iter(selected_dependent_variables.values())).name

        # Sanitize variable name: comma, bracket, and colon are not allowed in column names
        sanitized_dependent_variable = dependent_variable.replace("(", "_").replace(")", "").replace(",", "_")
        if sanitized_dependent_variable != dependent_variable:
            df.rename(columns={dependent_variable: sanitized_dependent_variable}, inplace=True)
            dependent_variable = sanitized_dependent_variable

        anova = pg.anova(
            data=df,
            dv=dependent_variable,
            between=selected_factor_names,
            detailed=True,
        ).round(5)

        effsize = self.eff_size[self.ui.comboBoxEffectSizeType.currentText()]
        padjust = self.p_adjustment[self.ui.comboBoxPAdjustment.currentText()]

        if len(selected_factor_names) > 2:
            html_template = """
                            <h2>{anova_header}</h2>
                            {anova}
                            """

            html = html_template.format(
                anova_header=anova_header,
                anova=anova.to_html(),
            )
        else:
            post_hoc_test = pg.pairwise_tests(
                data=df,
                dv=dependent_variable,
                between=selected_factor_names,
                return_desc=True,
                effsize=effsize,
                padjust=padjust,
                nan_policy="listwise",
            ).round(5)

            html_template = """
                            <h2>{anova_header}</h2>
                            {anova}
                            <h2>Pairwise post-hoc tests</h2>
                            {post_hoc_test}
                            """

            html = html_template.format(
                anova_header=anova_header,
                anova=anova.to_html(),
                post_hoc_test=post_hoc_test.to_html(),
            )

        self.ui.textEdit.document().setHtml(html)

    def _add_report(self):
        self.dataset.report += self.ui.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
