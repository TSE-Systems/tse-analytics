from typing import Optional

import pingouin as pg
from PySide6.QtWidgets import QWidget
from statsmodels.stats.multicomp import pairwise_tukeyhsd

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

        self.variable = ""
        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)

        self.ui.webView.settings().setAttribute(self.ui.webView.settings().WebAttribute.PluginsEnabled, False)
        self.ui.webView.settings().setAttribute(self.ui.webView.settings().WebAttribute.PdfViewerEnabled, False)
        self.ui.webView.setHtml("")

        self.ui.splitter.setSizes([2, 1])

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.__clear()
        self.ui.variableSelector.set_data(message.data.variables)

    def __on_clear_data(self, message: ClearDataMessage):
        self.__clear()

    def __clear(self):
        self.ui.variableSelector.clear()
        self.ui.canvas.clear()
        self.ui.webView.setHtml("")

    def __variable_changed(self, variable: str):
        self.variable = variable

    def __analyze(self):
        if Manager.data.selected_dataset is None or Manager.data.selected_factor is None:
            return

        factor_name = Manager.data.selected_factor.name
        df = Manager.data.selected_dataset.active_df[["Animal", factor_name, self.variable]]

        # Drop NaN rows
        df = df.dropna()

        homoscedasticity = pg.homoscedasticity(data=df, dv=self.variable, group=factor_name, center="mean")

        if homoscedasticity["equal_var"].values[0]:
            anova_header = "Classic one-way ANOVA"
            anova = pg.anova(data=df, dv=self.variable, between=factor_name, detailed=True)
        else:
            anova_header = "Welch one-way ANOVA"
            anova = pg.welch_anova(data=df, dv=self.variable, between=factor_name)

        # anova_header = "Repeated measures one-way ANOVA"
        # anova = pg.rm_anova(data=df, dv=self.variable, within=factor_name, subject='Animal', detailed=True)

        pt = pg.pairwise_tukey(dv=self.variable, between=factor_name, data=df)
        # self.webView.setHtml(pt.to_html())

        tukey = pairwise_tukeyhsd(
            endog=df[self.variable], groups=df[factor_name], alpha=0.05
        )  # Significance level

        html_template = """
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>Test for equality of variances between groups</h3>
                    {homoscedasticity}
                    <h3>{anova_header}</h3>
                    {anova}
                    <h3>Pairwise Comparison</h3>
                    {tukey}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            homoscedasticity=homoscedasticity.to_html(classes="mystyle"),
            anova_header=anova_header,
            anova=anova.to_html(classes="mystyle"),
            tukey=pt.to_html(classes="mystyle"),
        )
        self.ui.webView.setHtml(html)

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)
        tukey.plot_simultaneous(
            ax=ax,
            figsize=self.ui.canvas.figure.get_size_inches()
        )  # Plot group confidence intervals
        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
