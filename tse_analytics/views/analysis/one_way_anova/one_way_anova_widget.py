import pingouin as pg
from pyqttoast import ToastPreset
from PySide6.QtWidgets import QWidget
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core import messaging
from tse_analytics.core.helper import get_html_image, show_help
from tse_analytics.core.toaster import make_toast
from tse_analytics.css import style_descriptive_table
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.views.analysis.one_way_anova.one_way_anova_widget_ui import Ui_OneWayAnovaWidget


class OneWayAnovaWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_OneWayAnovaWidget()
        self.ui.setupUi(self)

        self.title = "One-way ANOVA"
        self.help_path = "one-way-anova.md"

        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

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

        df = self.dataset.get_anova_df(variables=selected_dependent_variables)

        dependent_variable = next(iter(selected_dependent_variables.values())).name
        factor_name = selected_factor_names[0]
        effsize = self.eff_size[self.ui.comboBoxEffectSizeType.currentText()]

        normality = pg.normality(df, group=factor_name, dv=dependent_variable).round(5)
        homoscedasticity = pg.homoscedasticity(df, group=factor_name, dv=dependent_variable).round(5)

        if homoscedasticity.loc["levene"]["equal_var"]:
            anova = pg.anova(
                data=df,
                dv=dependent_variable,
                between=factor_name,
                detailed=True,
            ).round(5)
            anova_header = "One-way classic ANOVA"

            post_hoc_test = pg.pairwise_tukey(
                data=df,
                dv=dependent_variable,
                between=factor_name,
                effsize=effsize,
            ).round(5)
            post_hoc_test_header = "Pairwise Tukey-HSD post-hoc test"
        else:
            anova = pg.welch_anova(
                data=df,
                dv=dependent_variable,
                between=factor_name,
            ).round(5)
            anova_header = "One-way Welch ANOVA"

            post_hoc_test = pg.pairwise_gameshowell(
                data=df,
                dv=dependent_variable,
                between=factor_name,
                effsize=effsize,
            ).round(5)
            post_hoc_test_header = "Pairwise Games-Howell post-hoc test"

        pairwise_tukeyhsd_res = pairwise_tukeyhsd(df[dependent_variable], df[factor_name])
        fig = pairwise_tukeyhsd_res.plot_simultaneous(ylabel="Group", xlabel=dependent_variable)
        img_html = get_html_image(fig)
        fig.clear()

        html_template = """
                <h1>Factor: {factor_name}</h1>
                <h2>Univariate normality test</h2>
                {normality}
                <h2>Homoscedasticity (equality of variances)</h2>
                {homoscedasticity}
                <h2>{anova_header}</h2>
                {anova}
                <h2>{post_hoc_test_header}</h2>
                {post_hoc_test}
                {img_html}
                """

        html = html_template.format(
            factor_name=factor_name,
            anova=anova.to_html(index=False),
            anova_header=anova_header,
            normality=normality.to_html(),
            homoscedasticity=homoscedasticity.to_html(),
            post_hoc_test=post_hoc_test.to_html(index=False),
            post_hoc_test_header=post_hoc_test_header,
            img_html=img_html,
        )
        self.ui.textEdit.document().setHtml(html)

    def _add_report(self):
        messaging.broadcast(messaging.AddToReportMessage(self, self.ui.textEdit.toHtml(), self.dataset))
