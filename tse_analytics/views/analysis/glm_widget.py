import pingouin as pg
import seaborn as sns
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.core.messaging.messages import DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.core.messaging.messenger_listener import MessengerListener
from tse_analytics.css import style
from tse_analytics.views.analysis.glm_widget_ui import Ui_GlmWidget
from tse_analytics.views.misc.toast import Toast


class GlmWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_GlmWidget()
        self.ui.setupUi(self)

        self.help_path = "glm.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.covariate = ""
        self.ui.variableSelectorCovariate.currentTextChanged.connect(self.__covariate_changed)

        self.response = ""
        self.ui.variableSelectorResponse.currentTextChanged.connect(self.__response_changed)

        self.plotToolbar = NavigationToolbar2QT(self.ui.canvas, self)
        self.plotToolbar.setIconSize(QSize(16, 16))
        self.ui.horizontalLayout.insertWidget(self.ui.horizontalLayout.count() - 1, self.plotToolbar)

        self.ui.splitter.setSizes([2, 1])

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.toolButtonAnalyse.setDisabled(message.data is None)
        self.__clear()
        if message.data is not None:
            self.ui.variableSelectorCovariate.set_data(message.data.variables)
            self.ui.variableSelectorResponse.set_data(message.data.variables)

    def __clear(self):
        self.ui.variableSelectorCovariate.clear()
        self.ui.variableSelectorResponse.clear()
        self.ui.webView.setHtml("")

    def __covariate_changed(self, covariate: str):
        self.covariate = covariate

    def __response_changed(self, response: str):
        self.response = response

    def __analyze(self):
        if Manager.data.selected_factor is None:
            Toast(text="Please select a factor first!", parent=self, duration=2000).show_toast()
            return

        factor_name = Manager.data.selected_factor.name

        variables = [self.response] if self.response == self.covariate else [self.response, self.covariate]
        df = Manager.data.get_current_df(variables=variables)

        df = df.groupby(by=["Animal"], as_index=False).agg({
            self.covariate: "mean",
            self.response: "mean",
            factor_name: "first",
        })

        facet_grid = sns.lmplot(data=df, x=self.covariate, y=self.response, hue=factor_name, robust=False)
        canvas = FigureCanvasQTAgg(facet_grid.figure)

        canvas.updateGeometry()
        canvas.draw()
        self.ui.splitter.replaceWidget(0, canvas)

        # Assign canvas to PlotToolbar
        self.plotToolbar.canvas = canvas

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
