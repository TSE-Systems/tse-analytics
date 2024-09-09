import pingouin as pg
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QTableWidgetItem, QWidget

from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import AddToReportMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.css import style_descriptive_table
from tse_analytics.views.analysis.anova_widget_ui import Ui_AnovaWidget
from tse_analytics.views.misc.notification import Notification


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

        self.ui.tableWidgetDependentVariable.setHorizontalHeaderLabels(["Name", "Unit", "Description"])
        self.ui.tableWidgetCovariates.setHorizontalHeaderLabels(["Name", "Unit", "Description"])

        self.ui.radioButtonOneWayAnova.toggled.connect(
            lambda toggled: self.ui.groupBoxCovariates.hide() if toggled else None
        )
        self.ui.radioButtonNWayAnova.toggled.connect(
            lambda toggled: self.ui.groupBoxCovariates.hide() if toggled else None
        )
        self.ui.radioButtonRMAnova.toggled.connect(
            lambda toggled: self.ui.groupBoxCovariates.hide() if toggled else None
        )
        self.ui.radioButtonMixedAnova.toggled.connect(
            lambda toggled: self.ui.groupBoxCovariates.hide() if toggled else None
        )
        self.ui.radioButtonAncova.toggled.connect(
            lambda toggled: self.ui.groupBoxCovariates.show() if toggled else None
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

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self._clear()
        if message.data is None:
            self.ui.pushButtonUpdate.setDisabled(True)
            self.ui.pushButtonAddReport.setDisabled(True)
            return

        self.ui.pushButtonUpdate.setDisabled(len(Manager.data.selected_dataset.factors) == 0)
        self.ui.pushButtonAddReport.setDisabled(len(Manager.data.selected_dataset.factors) == 0)

        self.ui.factorSelector.set_data(message.data.factors, add_empty_item=False)

        self.ui.tableWidgetDependentVariable.setRowCount(len(message.data.variables.values()))
        self.ui.tableWidgetCovariates.setRowCount(len(message.data.variables.values()))

        pal = self.ui.tableWidgetDependentVariable.palette()
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.Highlight,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight),
        )
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.HighlightedText,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText),
        )
        self.ui.tableWidgetDependentVariable.setPalette(pal)
        self.ui.tableWidgetCovariates.setPalette(pal)

        for i, variable in enumerate(message.data.variables.values()):
            self.ui.tableWidgetDependentVariable.setItem(i, 0, QTableWidgetItem(variable.name))
            self.ui.tableWidgetCovariates.setItem(i, 0, QTableWidgetItem(variable.name))

            self.ui.tableWidgetDependentVariable.setItem(i, 1, QTableWidgetItem(variable.unit))
            self.ui.tableWidgetCovariates.setItem(i, 1, QTableWidgetItem(variable.unit))

            self.ui.tableWidgetDependentVariable.setItem(i, 2, QTableWidgetItem(variable.description))
            self.ui.tableWidgetCovariates.setItem(i, 2, QTableWidgetItem(variable.description))

    def _clear(self):
        self.ui.pushButtonUpdate.setDisabled(True)
        self.ui.factorSelector.clear()
        self.ui.textEdit.document().clear()
        self.ui.tableWidgetDependentVariable.setRowCount(0)
        self.ui.tableWidgetCovariates.setRowCount(0)

    def _update(self):
        selected_dependent_variable_items = self.ui.tableWidgetDependentVariable.selectedItems()
        if len(selected_dependent_variable_items) == 0:
            Notification(text="Please select dependent variable.", parent=self, duration=2000).show_notification()
            return

        dependent_variable = selected_dependent_variable_items[0].text()

        if self.ui.radioButtonOneWayAnova.isChecked():
            self._analyze_one_way_anova(dependent_variable)
        elif self.ui.radioButtonNWayAnova.isChecked():
            self._analyze_n_way_anova(dependent_variable)
        elif self.ui.radioButtonRMAnova.isChecked():
            self._analyze_rm_anova(dependent_variable)
        elif self.ui.radioButtonMixedAnova.isChecked():
            self._analyze_mixed_anova(dependent_variable)
        elif self.ui.radioButtonAncova.isChecked():
            self._analyze_ancova(dependent_variable)

    def _analyze_one_way_anova(self, dependent_variable: str):
        selected_factor_name = self.ui.factorSelector.currentText()
        selected_factor = (
            Manager.data.selected_dataset.factors[selected_factor_name] if selected_factor_name != "" else None
        )
        if selected_factor is None:
            Notification(text="Please select factor.", parent=self, duration=2000).show_notification()
            return

        df = Manager.data.get_anova_df(variables=[dependent_variable])

        factor_name = selected_factor.name

        effsize = self.eff_size[self.ui.comboBoxEffectSizeType.currentText()]

        normality = pg.normality(df, group=factor_name, dv=dependent_variable).round(3)
        homoscedasticity = pg.homoscedasticity(df, group=factor_name, dv=dependent_variable).round(3)

        if homoscedasticity.loc["levene"]["equal_var"]:
            post_hoc_test = df.pairwise_tukey(dv=dependent_variable, between=factor_name, effsize=effsize).round(3)
            post_hoc_test_header = "Pairwise Tukey-HSD post-hoc test"

            anova = pg.anova(data=df, dv=dependent_variable, between=factor_name, detailed=True).round(3)
            anova_header = "One-way ANOVA"
        else:
            post_hoc_test = pg.pairwise_gameshowell(
                data=df, dv=dependent_variable, between=factor_name, effsize=effsize
            ).round(3)
            post_hoc_test_header = "Pairwise Games-Howell post-hoc test"

            anova = pg.welch_anova(data=df, dv=dependent_variable, between=factor_name).round(3)
            anova_header = "One-way Welch ANOVA"

        html_template = """
                <h1>Assumptions check</h1>
                <h2>Univariate normality test</h2>
                {normality}
                <h2>Homoscedasticity (equality of variance)</h2>
                {homoscedasticity}
                <h1>{anova_header}</h1>
                {anova}
                <h2>{post_hoc_test_header}</h2>
                {post_hoc_test}
                """

        html = html_template.format(
            anova=anova.to_html(),
            anova_header=anova_header,
            normality=normality.to_html(),
            homoscedasticity=homoscedasticity.to_html(),
            post_hoc_test=post_hoc_test.to_html(),
            post_hoc_test_header=post_hoc_test_header,
        )
        self.ui.textEdit.document().setHtml(html)

    def _analyze_n_way_anova(self, dependent_variable: str):
        df = Manager.data.get_anova_df(variables=[dependent_variable])

        factor_names = list(Manager.data.selected_dataset.factors.keys())
        match len(factor_names):
            case 1:
                anova_header = "One-way ANOVA"
            case 2:
                anova_header = "Two-way ANOVA"
            case 3:
                anova_header = "Three-way ANOVA"
            case _:
                anova_header = "Multi-way ANOVA"

        anova = pg.anova(data=df, dv=dependent_variable, between=factor_names, detailed=True).round(3)

        html_template = """
                <h1>{anova_header}</h1>
                {anova}
                """

        html = html_template.format(
            anova_header=anova_header,
            anova=anova.to_html(),
        )
        self.ui.textEdit.document().setHtml(html)

    def _analyze_rm_anova(self, dependent_variable: str):
        if not Manager.data.binning_params.apply or Manager.data.binning_params.mode == BinningMode.INTERVALS:
            Notification(
                text="Please apply binning in Dark/Light Cycles or Time Phases mode.", parent=self, duration=2000
            ).show_notification()
            return

        df = Manager.data.get_current_df(
            variables=[dependent_variable],
            split_mode=SplitMode.ANIMAL,
            selected_factor=None,
            dropna=True,
        )

        anova = pg.rm_anova(data=df, dv=dependent_variable, within="Bin", subject="Animal", detailed=True).round(3)

        padjust = self.p_adjustment[self.ui.comboBoxPAdjustment.currentText()]
        pairwise_tests = pg.pairwise_tests(
            data=df, dv=dependent_variable, within="Bin", subject="Animal", return_desc=True, padjust=padjust
        ).round(3)

        html_template = """
                <h1>Repeated measures one-way ANOVA</h1>
                {anova}
                <h2>Pairwise tests</h2>
                {pairwise_tests}
                """

        html = html_template.format(
            anova=anova.to_html(),
            pairwise_tests=pairwise_tests.to_html(),
        )
        self.ui.textEdit.document().setHtml(html)

    def _analyze_mixed_anova(self, dependent_variable: str):
        selected_factor_name = self.ui.factorSelector.currentText()
        selected_factor = (
            Manager.data.selected_dataset.factors[selected_factor_name] if selected_factor_name != "" else None
        )
        if selected_factor is None:
            Notification(text="Please select factor.", parent=self, duration=2000).show_notification()
            return

        if not Manager.data.binning_params.apply or Manager.data.binning_params.mode == BinningMode.INTERVALS:
            Notification(
                text="Please apply binning in Dark/Light Cycles or Time Phases mode.", parent=self, duration=2000
            ).show_notification()
            return

        factor_name = selected_factor.name

        df = Manager.data.get_current_df(
            variables=[dependent_variable],
            split_mode=SplitMode.ANIMAL,
            selected_factor=None,
            dropna=True,
        )

        anova = pg.mixed_anova(
            data=df,
            dv=dependent_variable,
            between=factor_name,
            within="Bin",
            subject="Animal",
        ).round(3)

        padjust = self.p_adjustment[self.ui.comboBoxPAdjustment.currentText()]
        pairwise_tests = pg.pairwise_tests(
            data=df, dv=dependent_variable, within="Bin", subject="Animal", return_desc=True, padjust=padjust
        ).round(3)

        html_template = """
                <h1>Mixed-design ANOVA</h1>
                {anova}
                <h2>Pairwise tests</h2>
                {pairwise_tests}
                """

        html = html_template.format(
            anova=anova.to_html(),
            pairwise_tests=pairwise_tests.to_html(),
        )
        self.ui.textEdit.document().setHtml(html)

    def _analyze_ancova(self, dependent_variable: str):
        selected_factor_name = self.ui.factorSelector.currentText()
        selected_factor = (
            Manager.data.selected_dataset.factors[selected_factor_name] if selected_factor_name != "" else None
        )
        if selected_factor is None:
            Notification(text="Please select factor.", parent=self, duration=2000).show_notification()
            return

        factor_name = selected_factor.name

        selected_covariates_items = self.ui.tableWidgetCovariates.selectedItems()
        selected_covariates = []
        for i in range(0, len(selected_covariates_items) // 3):
            selected_covariates.append(selected_covariates_items[i * 3].text())

        variables = [dependent_variable] + selected_covariates

        df = Manager.data.get_anova_df(variables=variables)

        padjust = self.p_adjustment[self.ui.comboBoxPAdjustment.currentText()]
        effsize = self.eff_size[self.ui.comboBoxEffectSizeType.currentText()]

        ancova = pg.ancova(data=df, dv=dependent_variable, covar=selected_covariates, between=factor_name).round(3)
        pairwise_tests = pg.pairwise_tests(
            data=df,
            dv=dependent_variable,
            between=factor_name,
            effsize=effsize,
            padjust=padjust,
            return_desc=True,
        ).round(3)

        html_template = """
                        <h1>ANCOVA</h1>
                        {ancova}
                        <h2>Pairwise tests</h2>
                        {pairwise_tests}
                        """

        html = html_template.format(
            ancova=ancova.to_html(),
            pairwise_tests=pairwise_tests.to_html(),
        )
        self.ui.textEdit.document().setHtml(html)

    def _add_report(self):
        Manager.messenger.broadcast(AddToReportMessage(self, self.ui.textEdit.toHtml()))
