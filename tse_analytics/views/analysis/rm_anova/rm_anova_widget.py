import pandas as pd
import pingouin as pg
from pyqttoast import ToastPreset
from PySide6.QtWidgets import QMessageBox, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import show_help
from tse_analytics.core.toaster import make_toast
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.analysis.rm_anova.rm_anova_widget_ui import Ui_RMAnovaWidget


class RMAnovaWidget(QWidget):
    def __init__(self, dataset: Dataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_RMAnovaWidget()
        self.ui.setupUi(self)

        self.title = "Repeated Measures ANOVA"
        self.help_path = "Repeated-Measures-ANOVA.md"

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

        do_pairwise_tests = True
        if not self.dataset.binning_settings.apply:
            make_toast(
                self,
                self.title,
                "Please apply a proper binning first.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return
        elif self.dataset.binning_settings.mode == BinningMode.INTERVALS:
            if (
                QMessageBox.question(
                    self,
                    "Perform pairwise tests?",
                    "Calculation of pairwise tests with many time bins can take a long time!",
                )
                == QMessageBox.StandardButton.No
            ):
                do_pairwise_tests = False

        df = self.dataset.get_current_df(
            variables=selected_dependent_variables,
            split_mode=SplitMode.ANIMAL,
            selected_factor_name=None,
            dropna=True,
        )

        dependent_variable = next(iter(selected_dependent_variables.values())).name

        spher, W, chisq, dof, pval = pg.sphericity(
            data=df,
            dv=dependent_variable,
            within="Bin",
            subject="Animal",
            method="mauchly",
        )
        sphericity = pd.DataFrame(
            [[spher, W, chisq, dof, pval]],
            columns=["Sphericity", "W", "Chi-square", "DOF", "p-value"],
        ).round(5)

        anova = pg.rm_anova(
            data=df,
            dv=dependent_variable,
            within="Bin",
            subject="Animal",
            detailed=True,
        ).round(5)

        if do_pairwise_tests:
            effsize = self.eff_size[self.ui.comboBoxEffectSizeType.currentText()]
            padjust = self.p_adjustment[self.ui.comboBoxPAdjustment.currentText()]

            pairwise_tests = pg.pairwise_tests(
                data=df,
                dv=dependent_variable,
                within="Bin",
                subject="Animal",
                return_desc=True,
                effsize=effsize,
                padjust=padjust,
            ).round(5)

            html_template = """
                                        <h2>Sphericity test</h2>
                                        {sphericity}
                                        <h2>Repeated measures one-way ANOVA</h2>
                                        {anova}
                                        <h2>Pairwise post-hoc tests</h2>
                                        {pairwise_tests}
                                        """

            html = html_template.format(
                sphericity=sphericity.to_html(),
                anova=anova.to_html(),
                pairwise_tests=pairwise_tests.to_html(),
            )
        else:
            html_template = """
                                        <h2>Sphericity test</h2>
                                        {sphericity}
                                        <h2>Repeated measures one-way ANOVA</h2>
                                        {anova}
                                        """

            html = html_template.format(
                sphericity=sphericity.to_html(),
                anova=anova.to_html(),
            )

        self.ui.textEdit.document().setHtml(html)

    def _add_report(self):
        self.dataset.report += self.ui.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.dataset))
