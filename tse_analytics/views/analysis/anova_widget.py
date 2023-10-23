from typing import Optional

import pingouin as pg
from PySide6.QtWidgets import QWidget

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

        # self.ui.webView.settings().setAttribute(self.ui.webView.settings().WebAttribute.PluginsEnabled, False)
        # self.ui.webView.settings().setAttribute(self.ui.webView.settings().WebAttribute.PdfViewerEnabled, False)
        # self.ui.webView.setHtml("")

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
        self.ui.webView.setHtml("")

    def __variable_changed(self, variable: str):
        self.variable = variable

    def __analyze(self):
        if Manager.data.selected_dataset is None or len(Manager.data.selected_dataset.factors) == 0:
            return

        df = Manager.data.get_anova_df(variables=[self.variable])

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
        anova = pg.anova(data=df, dv=self.variable, between=factor_names, detailed=True).round(3)

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
