import pandas as pd
import pingouin as pg
from PySide6.QtWidgets import QWidget, QAbstractItemView, QMessageBox
from pyqttoast import ToastPreset
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.shared import SplitMode, Variable
from tse_analytics.core.helper import show_help, get_html_image, make_toast
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import AddToReportMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.css import style_descriptive_table
from tse_analytics.views.analysis.anova_widget_ui import Ui_AnovaWidget


class AnovaWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_AnovaWidget()
        self.ui.setupUi(self)

        self.help_path = "anova.md"
        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonAddReport.clicked.connect(self._add_report)

        self.ui.groupBoxCovariates.hide()
        self.ui.groupBoxPAdjustment.hide()

        self.ui.tableWidgetCovariates.set_selection_mode(QAbstractItemView.SelectionMode.MultiSelection)

        self.ui.radioButtonOneWayAnova.toggled.connect(
            lambda toggled: self._set_options(True, False, False, False) if toggled else None
        )
        self.ui.radioButtonNWayAnova.toggled.connect(
            lambda toggled: self._set_options(True, False, True, True) if toggled else None
        )
        self.ui.radioButtonRMAnova.toggled.connect(
            lambda toggled: self._set_options(False, False, False, False) if toggled else None
        )
        self.ui.radioButtonMixedAnova.toggled.connect(
            lambda toggled: self._set_options(True, False, False, True) if toggled else None
        )
        self.ui.radioButtonAncova.toggled.connect(
            lambda toggled: self._set_options(True, True, False, True) if toggled else None
        )

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
            "Pearson correlation coefficient": "r",
            "Eta-square": "eta-square",
            "Odds ratio": "odds-ratio",
            "Area Under the Curve": "AUC",
            "Common Language Effect Size": "CLES",
        }
        self.ui.comboBoxEffectSizeType.addItems(self.eff_size.keys())
        self.ui.comboBoxEffectSizeType.setCurrentText("Hedges g")

        self.ui.textEdit.document().setDefaultStyleSheet(style_descriptive_table)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)

    def _set_options(
        self, show_factors: bool, show_covariates: bool, multi_factor_selection: bool, show_p_adjustment: bool
    ):
        if show_factors:
            self.ui.groupBoxFactors.show()
        else:
            self.ui.groupBoxFactors.hide()

        if show_covariates:
            self.ui.groupBoxCovariates.show()
        else:
            self.ui.groupBoxCovariates.hide()

        if show_p_adjustment:
            self.ui.groupBoxPAdjustment.show()
        else:
            self.ui.groupBoxPAdjustment.hide()

        self.ui.tableWidgetFactors.set_selection_mode(
            QAbstractItemView.SelectionMode.MultiSelection
            if multi_factor_selection
            else QAbstractItemView.SelectionMode.SingleSelection
        )

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self._clear()
        if message.data is None:
            self.ui.pushButtonUpdate.setDisabled(True)
            self.ui.pushButtonAddReport.setDisabled(True)
            return

        self.ui.pushButtonUpdate.setDisabled(len(Manager.data.selected_dataset.factors) == 0)
        self.ui.pushButtonAddReport.setDisabled(len(Manager.data.selected_dataset.factors) == 0)

        self.ui.tableWidgetFactors.set_data(message.data.factors)
        self.ui.tableWidgetDependentVariable.set_data(message.data.variables)
        self.ui.tableWidgetCovariates.set_data(message.data.variables)

    def _clear(self):
        self.ui.pushButtonUpdate.setDisabled(True)
        self.ui.textEdit.document().clear()
        self.ui.tableWidgetFactors.clear_data()
        self.ui.tableWidgetDependentVariable.clear_data()
        self.ui.tableWidgetCovariates.clear_data()

    def _update(self):
        selected_dependent_variables = self.ui.tableWidgetDependentVariable.get_selected_variables_dict()
        if len(selected_dependent_variables) == 0:
            make_toast(
                self,
                "ANOVA",
                "Please select dependent variable.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        if self.ui.radioButtonOneWayAnova.isChecked():
            self._analyze_one_way_anova(selected_dependent_variables)
        elif self.ui.radioButtonNWayAnova.isChecked():
            self._analyze_n_way_anova(selected_dependent_variables)
        elif self.ui.radioButtonRMAnova.isChecked():
            self._analyze_rm_anova(selected_dependent_variables)
        elif self.ui.radioButtonMixedAnova.isChecked():
            self._analyze_mixed_anova(selected_dependent_variables)
        elif self.ui.radioButtonAncova.isChecked():
            self._analyze_ancova(selected_dependent_variables)

    def _analyze_one_way_anova(self, selected_dependent_variables: dict[str, Variable]):
        selected_factor_names = self.ui.tableWidgetFactors.get_selected_factor_names()
        if len(selected_factor_names) != 1:
            make_toast(
                self,
                "One-way ANOVA",
                "Please select a single factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        df = Manager.data.get_anova_df(variables=selected_dependent_variables)

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

    def _analyze_n_way_anova(self, selected_dependent_variables: dict[str, Variable]):
        selected_factor_names = self.ui.tableWidgetFactors.get_selected_factor_names()
        if len(selected_factor_names) < 2:
            make_toast(
                self,
                "N-way ANOVA",
                "Please select several factors.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        df = Manager.data.get_anova_df(variables=selected_dependent_variables)

        dependent_variable = next(iter(selected_dependent_variables.values())).name
        anova = pg.anova(
            data=df,
            dv=dependent_variable,
            between=selected_factor_names,
            detailed=True,
        ).round(5)

        effsize = self.eff_size[self.ui.comboBoxEffectSizeType.currentText()]
        padjust = self.p_adjustment[self.ui.comboBoxPAdjustment.currentText()]

        post_hoc_test = pg.pairwise_tests(
            data=df,
            dv=dependent_variable,
            between=selected_factor_names,
            return_desc=True,
            effsize=effsize,
            padjust=padjust,
        ).round(5)

        html_template = """
                <h2>{anova_header}</h2>
                {anova}
                <h2>Pairwise post-hoc tests</h2>
                {post_hoc_test}
                """

        match len(selected_factor_names):
            case 2:
                anova_header = "Two-way ANOVA"
            case 3:
                anova_header = "Three-way ANOVA"
            case _:
                anova_header = "Multi-way ANOVA"

        html = html_template.format(
            anova_header=anova_header,
            anova=anova.to_html(),
            post_hoc_test=post_hoc_test.to_html(),
        )
        self.ui.textEdit.document().setHtml(html)

    def _analyze_rm_anova(self, selected_dependent_variables: dict[str, Variable]):
        do_pairwise_tests = True
        if not Manager.data.selected_dataset.binning_settings.apply:
            make_toast(
                self,
                "Repeated Measures ANOVA",
                "Please apply a proper binning first.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return
        elif Manager.data.selected_dataset.binning_settings.mode == BinningMode.INTERVALS:
            if (
                QMessageBox.question(
                    self,
                    "Perform pairwise tests?",
                    "Calculation of pairwise tests with many time bins can take a long time!",
                )
                == QMessageBox.StandardButton.No
            ):
                do_pairwise_tests = False

        df = Manager.data.get_current_df(
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

            pairwise_tests = pg.pairwise_tests(
                data=df,
                dv=dependent_variable,
                within="Bin",
                subject="Animal",
                return_desc=True,
                effsize=effsize,
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

    def _analyze_mixed_anova(self, selected_dependent_variables: dict[str, Variable]):
        selected_factor_names = self.ui.tableWidgetFactors.get_selected_factor_names()
        if len(selected_factor_names) != 1:
            make_toast(
                self,
                "Mixed ANOVA",
                "Please select a single factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        do_pairwise_tests = True
        if not Manager.data.selected_dataset.binning_settings.apply:
            make_toast(
                self,
                "Mixed ANOVA",
                "Please apply a proper binning first.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return
        elif Manager.data.selected_dataset.binning_settings.mode == BinningMode.INTERVALS:
            if (
                QMessageBox.question(
                    self,
                    "Perform pairwise tests?",
                    "Calculation of pairwise tests with many time bins can take a long time!",
                )
                == QMessageBox.StandardButton.No
            ):
                do_pairwise_tests = False

        factor_name = selected_factor_names[0]

        df = Manager.data.get_current_df(
            variables=selected_dependent_variables,
            split_mode=SplitMode.ANIMAL,
            selected_factor_name=None,
            dropna=True,
        )

        dependent_variable = next(iter(selected_dependent_variables.values())).name

        anova = pg.mixed_anova(
            data=df,
            dv=dependent_variable,
            between=factor_name,
            within="Bin",
            subject="Animal",
        ).round(5)

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

        if do_pairwise_tests:
            effsize = self.eff_size[self.ui.comboBoxEffectSizeType.currentText()]

            pairwise_tests = pg.pairwise_tests(
                data=df,
                dv=dependent_variable,
                within="Bin",
                between=factor_name,
                subject="Animal",
                return_desc=True,
                effsize=effsize,
            ).round(5)

            html_template = """
                                        <h2>Sphericity test</h2>
                                        {sphericity}
                                        <h2>Mixed-design ANOVA</h2>
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
                                        <h2>Mixed-design ANOVA</h2>
                                        {anova}
                                        """

            html = html_template.format(
                sphericity=sphericity.to_html(),
                anova=anova.to_html(),
            )

        self.ui.textEdit.document().setHtml(html)

    def _analyze_ancova(self, selected_dependent_variables: dict[str, Variable]):
        selected_factor_names = self.ui.tableWidgetFactors.get_selected_factor_names()
        if len(selected_factor_names) != 1:
            make_toast(
                self,
                "ANCOVA",
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

        df = Manager.data.get_anova_df(variables=variables)

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
        Manager.messenger.broadcast(AddToReportMessage(self, self.ui.textEdit.toHtml()))
