from typing import Optional

import pingouin as pg
from PySide6.QtWidgets import QWidget

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.messaging.messages import DatasetChangedMessage, ClearDataMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.ancova_widget_ui import Ui_AncovaWidget


class AncovaWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_AncovaWidget()
        self.ui.setupUi(self)

        self.help_path = "docs/ancova.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.covariate = ""
        self.ui.variableSelectorCovariate.currentTextChanged.connect(self.__covariate_current_text_changed)

        self.response = ""
        self.ui.variableSelectorResponse.currentTextChanged.connect(self.__response_current_text_changed)

        # self.ui.webView.settings().setAttribute(self.ui.webView.settings().WebAttribute.PluginsEnabled, False)
        # self.ui.webView.settings().setAttribute(self.ui.webView.settings().WebAttribute.PdfViewerEnabled, False)
        # self.ui.webView.setHtml("")

        self.ui.splitter.setSizes([2, 1])

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.__clear()
        self.ui.variableSelectorCovariate.set_data(message.data.variables)
        self.ui.variableSelectorResponse.set_data(message.data.variables)

    def __on_clear_data(self, message: ClearDataMessage):
        self.__clear()

    def __clear(self):
        self.ui.variableSelectorCovariate.clear()
        self.ui.variableSelectorResponse.clear()
        self.ui.webView.setHtml("")
        self.ui.canvas.clear()

    def __covariate_current_text_changed(self, covariate: str):
        self.covariate = covariate

    def __response_current_text_changed(self, response: str):
        self.response = response

    def __analyze(self):
        if Manager.data.selected_dataset is None or Manager.data.selected_factor is None:
            return

        factor_name = Manager.data.selected_factor.name

        df = Manager.data.selected_dataset.active_df

        ancova = pg.ancova(data=df, dv=self.response, covar=self.covariate, between=factor_name)

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
