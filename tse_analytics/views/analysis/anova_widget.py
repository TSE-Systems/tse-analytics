from typing import Optional

import pingouin as pg
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMessageBox

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.messaging.messages import ClearDataMessage, DatasetChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.anova_widget_ui import Ui_AnovaWidget


class AnovaWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_AnovaWidget()
        self.ui.setupUi(self)

        self.help_path = "docs/anova.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.ui.groupBoxCovariates.hide()

        self.ui.tableWidgetDependentVariable.setHorizontalHeaderLabels(["Name", "Unit", "Description"])
        self.ui.tableWidgetCovariates.setHorizontalHeaderLabels(["Name", "Unit", "Description"])

        self.ui.radioButtonAnova.toggled.connect(self.__anova_mode_activated)
        self.ui.radioButtonRMAnova.toggled.connect(self.__rm_anova_mode_activated)
        self.ui.radioButtonMixedAnova.toggled.connect(self.__mixed_anova_mode_activated)
        self.ui.radioButtonAncova.toggled.connect(self.__ancova_mode_activated)

        # self.ui.splitter.setSizes((1, 1))

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)

    def __anova_mode_activated(self):
        self.ui.groupBoxCovariates.hide()

    def __rm_anova_mode_activated(self):
        self.ui.groupBoxCovariates.hide()

    def __mixed_anova_mode_activated(self):
        self.ui.groupBoxCovariates.hide()

    def __ancova_mode_activated(self):
        self.ui.groupBoxCovariates.show()

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.__clear()

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

    def __on_clear_data(self, message: ClearDataMessage):
        self.__clear()

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

        if self.ui.radioButtonAnova.isChecked():
            self.__analyze_anova(dependent_variable)
        elif self.ui.radioButtonRMAnova.isChecked():
            self.__analyze_rm_anova(dependent_variable)
        elif self.ui.radioButtonMixedAnova.isChecked():
            self.__analyze_mixed_anova(dependent_variable)
        elif self.ui.radioButtonAncova.isChecked():
            self.__analyze_ancova(dependent_variable)

    def __analyze_anova(self, dependent_variable: str):
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

        anova = pg.anova(data=df, dv=dependent_variable, between=factor_names, detailed=True).round(6)

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
        df = Manager.data.get_current_df(variables=[dependent_variable], dropna=True)

        anova = pg.rm_anova(data=df, dv=dependent_variable, within="Bin", subject="Animal", detailed=True).round(6)

        html_template = """
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>Repeated measures one-way ANOVA</h3>
                    {anova}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            anova=anova.to_html(classes="mystyle"),
        )
        self.ui.webView.setHtml(html)

    def __analyze_mixed_anova(self, dependent_variable: str):
        if Manager.data.selected_factor is None:
            return

        factor_name = Manager.data.selected_factor.name

        df = Manager.data.get_current_df(variables=[dependent_variable], dropna=True)

        anova = pg.mixed_anova(
            data=df, dv=dependent_variable, between=factor_name, within="Bin", subject="Animal"
        ).round(6)

        html_template = """
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>Mixed-design ANOVA</h3>
                    {anova}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            anova=anova.to_html(classes="mystyle"),
        )
        self.ui.webView.setHtml(html)

    def __analyze_ancova(self, dependent_variable: str):
        if Manager.data.selected_factor is None:
            return

        factor_name = Manager.data.selected_factor.name

        selected_covariates_items = self.ui.tableWidgetCovariates.selectedItems()
        selected_covariates = []
        for i in range(0, len(selected_covariates_items) // 3):
            selected_covariates.append(selected_covariates_items[i * 3].text())

        variables = [dependent_variable] + selected_covariates

        df = Manager.data.get_anova_df(variables=variables)

        ancova = pg.ancova(data=df, dv=dependent_variable, covar=selected_covariates, between=factor_name).round(6)

        html_template = """
                        <html>
                          <head>
                            {style}
                          </head>
                          <body>
                            <h3>ANCOVA</h3>
                            {ancova}
                          </body>
                        </html>
                        """

        html = html_template.format(
            style=style,
            ancova=ancova.to_html(classes="mystyle"),
        )
        self.ui.webView.setHtml(html)
