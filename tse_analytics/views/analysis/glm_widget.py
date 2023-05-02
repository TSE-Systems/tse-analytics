from typing import Optional

import pingouin as pg
import seaborn as sns
from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.messaging.messages import DatasetChangedMessage, ClearDataMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.glm_widget_ui import Ui_GlmWidget
from tse_datatools.data.variable import Variable


class GlmWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_GlmWidget()
        self.ui.setupUi(self)

        self.help_path = "docs/glm.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.covariate = ""
        self.ui.variableSelectorCovariate.currentTextChanged.connect(self.__covariate_changed)

        self.response = ""
        self.ui.variableSelectorResponse.currentTextChanged.connect(self.__response_changed)

        # self.ui.webView.settings().setAttribute(self.ui.webView.settings().WebAttribute.PluginsEnabled, False)
        # self.ui.webView.settings().setAttribute(self.ui.webView.settings().WebAttribute.PdfViewerEnabled, False)
        # self.ui.webView.setHtml("")

        self.ui.splitter.setSizes([2, 1])

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self.__on_clear_data)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.__clear()
        covariate_variables = message.data.variables.copy()
        covariate_variables["Weight"] = Variable("Weight", "[g]", "Animal weight")
        self.ui.variableSelectorCovariate.set_data(covariate_variables)
        self.ui.variableSelectorResponse.set_data(message.data.variables)

    def __on_clear_data(self, message: ClearDataMessage):
        self.__clear()

    def __clear(self):
        self.ui.variableSelectorCovariate.clear()
        self.ui.variableSelectorResponse.clear()
        self.ui.webView.setHtml("")

    def __covariate_changed(self, covariate: str):
        self.covariate = covariate

    def __response_changed(self, response: str):
        self.response = response

    def __analyze(self):
        if Manager.data.selected_dataset is None or Manager.data.selected_factor is None:
            return

        factor_name = Manager.data.selected_factor.name

        df = Manager.data.selected_dataset.active_df.copy()
        if self.covariate == "Weight":
            df = df.groupby(by=["Animal"], as_index=False).agg({self.response: "mean", factor_name: "first"})
        else:
            df = df.groupby(by=["Animal"], as_index=False).agg(
                {self.covariate: "mean", self.response: "mean", factor_name: "first"}
            )

        if self.covariate == "Weight":
            df["Weight"] = df["Animal"].astype(float)
            weights = {}
            for animal in Manager.data.selected_dataset.animals.values():
                weights[animal.id] = animal.weight
            df = df.replace({"Weight": weights})

        facet_grid = sns.lmplot(data=df, x=self.covariate, y=self.response, hue=factor_name, robust=False)
        canvas = FigureCanvasQTAgg(facet_grid.figure)
        canvas.updateGeometry()
        canvas.draw()
        self.ui.splitter.replaceWidget(0, canvas)

        glm = pg.linear_regression(df[[self.covariate]], df[self.response])

        html_template = """
                <html>
                  <head>
                    {style}
                  </head>
                  <body>
                    <h3>GLM</h3>
                    {glm}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            glm=glm.to_html(classes="mystyle"),
        )
        self.ui.webView.setHtml(html)
