import pingouin as pg
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QWidget

from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.css import style
from tse_analytics.views.analysis.anova_widget_ui import Ui_AnovaWidget


class AnovaWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_AnovaWidget()
        self.ui.setupUi(self)

        self.help_path = "anova.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.ui.groupBoxCovariates.hide()

        self.ui.tableWidgetDependentVariable.setHorizontalHeaderLabels(["Name", "Unit", "Description"])
        self.ui.tableWidgetCovariates.setHorizontalHeaderLabels(["Name", "Unit", "Description"])

        self.ui.radioButtonOneWayAnova.toggled.connect(lambda: self.ui.groupBoxCovariates.hide())
        self.ui.radioButtonNWayAnova.toggled.connect(lambda: self.ui.groupBoxCovariates.hide())
        self.ui.radioButtonRMAnova.toggled.connect(lambda: self.ui.groupBoxCovariates.hide())
        self.ui.radioButtonMixedAnova.toggled.connect(lambda: self.ui.groupBoxCovariates.hide())
        self.ui.radioButtonAncova.toggled.connect(lambda: self.ui.groupBoxCovariates.show())

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

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.__clear()
        if message.data is None:
            self.ui.toolButtonAnalyse.setDisabled(True)
            return

        self.ui.toolButtonAnalyse.setDisabled(len(Manager.data.selected_dataset.factors) == 0)

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

    def __clear(self):
        self.ui.toolButtonAnalyse.setDisabled(True)
        self.ui.webView.setHtml("")
        self.ui.tableWidgetDependentVariable.setRowCount(0)
        self.ui.tableWidgetCovariates.setRowCount(0)

    def __analyze(self):
        selected_dependent_variable_items = self.ui.tableWidgetDependentVariable.selectedItems()
        if len(selected_dependent_variable_items) == 0:
            QMessageBox.warning(
                self,
                "Cannot perform analysis!",
                "Please select dependent variable.",
                buttons=QMessageBox.StandardButton.Abort,
                defaultButton=QMessageBox.StandardButton.Abort,
            )
            return

        dependent_variable = selected_dependent_variable_items[0].text()

        if self.ui.radioButtonOneWayAnova.isChecked():
            self.__analyze_one_way_anova(dependent_variable)
        elif self.ui.radioButtonNWayAnova.isChecked():
            self.__analyze_n_way_anova(dependent_variable)
        elif self.ui.radioButtonRMAnova.isChecked():
            self.__analyze_rm_anova(dependent_variable)
        elif self.ui.radioButtonMixedAnova.isChecked():
            self.__analyze_mixed_anova(dependent_variable)
        elif self.ui.radioButtonAncova.isChecked():
            self.__analyze_ancova(dependent_variable)

    def __analyze_one_way_anova(self, dependent_variable: str):
        if Manager.data.selected_factor is None:
            QMessageBox.warning(
                self,
                "Cannot perform analysis!",
                "Please select one factor.",
                buttons=QMessageBox.StandardButton.Abort,
                defaultButton=QMessageBox.StandardButton.Abort,
            )
            return

        df = Manager.data.get_anova_df(variables=[dependent_variable])

        factor_name = Manager.data.selected_factor.name

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
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>Assumptions check</h3>
                    <h4>Univariate normality test</h4>
                    {normality}
                    <h4>Homoscedasticity (equality of variance)</h4>
                    {homoscedasticity}
                    <h3>{anova_header}</h3>
                    {anova}
                    <h3>{post_hoc_test_header}</h3>
                    {post_hoc_test}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            anova=anova.to_html(classes="mystyle"),
            anova_header=anova_header,
            normality=normality.to_html(classes="mystyle"),
            homoscedasticity=homoscedasticity.to_html(classes="mystyle"),
            post_hoc_test=post_hoc_test.to_html(classes="mystyle"),
            post_hoc_test_header=post_hoc_test_header,
        )
        self.ui.webView.setHtml(html)

    def __analyze_n_way_anova(self, dependent_variable: str):
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
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>{anova_header}</h3>
                    {anova}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            anova_header=anova_header,
            anova=anova.to_html(classes="mystyle"),
        )
        self.ui.webView.setHtml(html)

    def __analyze_rm_anova(self, dependent_variable: str):
        if not Manager.data.binning_params.apply or Manager.data.binning_params.mode == BinningMode.INTERVALS:
            QMessageBox.warning(
                self,
                "Cannot perform analysis!",
                "Please apply binning in Dark/Light Cycles or Time Phases mode.",
                buttons=QMessageBox.StandardButton.Abort,
                defaultButton=QMessageBox.StandardButton.Abort,
            )
            return

        df = Manager.data.get_current_df(variables=[dependent_variable], dropna=True)

        anova = pg.rm_anova(data=df, dv=dependent_variable, within="Bin", subject="Animal", detailed=True).round(3)

        padjust = self.p_adjustment[self.ui.comboBoxPAdjustment.currentText()]
        pairwise_tests = pg.pairwise_tests(
            data=df, dv=dependent_variable, within="Bin", subject="Animal", return_desc=True, padjust=padjust
        ).round(3)

        html_template = """
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>Repeated measures one-way ANOVA</h3>
                    {anova}
                    <h3>Pairwise tests</h3>
                    {pairwise_tests}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            anova=anova.to_html(classes="mystyle"),
            pairwise_tests=pairwise_tests.to_html(classes="mystyle"),
        )
        self.ui.webView.setHtml(html)

    def __analyze_mixed_anova(self, dependent_variable: str):
        if Manager.data.selected_factor is None:
            QMessageBox.warning(
                self,
                "Cannot perform analysis!",
                "Please select one factor.",
                buttons=QMessageBox.StandardButton.Abort,
                defaultButton=QMessageBox.StandardButton.Abort,
            )
            return

        if not Manager.data.binning_params.apply or Manager.data.binning_params.mode == BinningMode.INTERVALS:
            QMessageBox.warning(
                self,
                "Cannot perform analysis!",
                "Please apply binning in Dark/Light Cycles or Time Phases mode.",
                buttons=QMessageBox.StandardButton.Abort,
                defaultButton=QMessageBox.StandardButton.Abort,
            )
            return

        factor_name = Manager.data.selected_factor.name

        df = Manager.data.get_current_df(variables=[dependent_variable], dropna=True)

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
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>Mixed-design ANOVA</h3>
                    {anova}
                    <h3>Pairwise tests</h3>
                    {pairwise_tests}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            anova=anova.to_html(classes="mystyle"),
            pairwise_tests=pairwise_tests.to_html(classes="mystyle"),
        )
        self.ui.webView.setHtml(html)

    def __analyze_ancova(self, dependent_variable: str):
        if Manager.data.selected_factor is None:
            QMessageBox.warning(
                self,
                "Cannot perform analysis!",
                "Please select one factor.",
                buttons=QMessageBox.StandardButton.Abort,
                defaultButton=QMessageBox.StandardButton.Abort,
            )
            return

        factor_name = Manager.data.selected_factor.name

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
                        <html>
                          <head>
                            {style}
                          </head>
                          <body>
                            <h3>ANCOVA</h3>
                            {ancova}
                            <h3>Pairwise tests</h3>
                            {pairwise_tests}
                          </body>
                        </html>
                        """

        html = html_template.format(
            style=style,
            ancova=ancova.to_html(classes="mystyle"),
            pairwise_tests=pairwise_tests.to_html(classes="mystyle"),
        )
        self.ui.webView.setHtml(html)
