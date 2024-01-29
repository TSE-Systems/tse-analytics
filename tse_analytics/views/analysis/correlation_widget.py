import pingouin as pg
import seaborn as sns
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget
from tse_analytics.analysis.grouping_mode import GroupingMode

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.messaging.messages import DatasetChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.correlation_widget_ui import Ui_CorrelationWidget
from tse_analytics.views.misc.toast import Toast


class CorrelationWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_CorrelationWidget()
        self.ui.setupUi(self)

        self.help_path = "correlation.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

        self.x_var = ""
        self.ui.variableSelectorX.currentTextChanged.connect(self.__x_current_text_changed)

        self.y_var = ""
        self.ui.variableSelectorY.currentTextChanged.connect(self.__y_current_text_changed)

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
            self.ui.variableSelectorX.set_data(message.data.variables)
            self.ui.variableSelectorY.set_data(message.data.variables)

    def __clear(self):
        self.ui.variableSelectorX.clear()
        self.ui.variableSelectorY.clear()
        self.ui.webView.setHtml("")

    def __x_current_text_changed(self, x: str):
        self.x_var = x

    def __y_current_text_changed(self, y: str):
        self.y_var = y

    def __analyze(self):
        if Manager.data.grouping_mode == GroupingMode.FACTORS and Manager.data.selected_factor is None:
            Toast(text="Please select a factor first!", parent=self, duration=2000).show_toast()
            return

        variables = [self.x_var] if self.x_var == self.y_var else [self.x_var, self.y_var]
        df = Manager.data.get_current_df(calculate_error=False, variables=variables)

        match Manager.data.grouping_mode:
            case GroupingMode.FACTORS:
                grouping = Manager.data.selected_factor.name
            case GroupingMode.RUNS:
                grouping = "Run"
            case _:
                df["Animal"] = df["Animal"].cat.remove_unused_categories()
                grouping = "Animal"

        joint_grid = sns.jointplot(data=df, x=self.x_var, y=self.y_var, hue=grouping)
        joint_grid.fig.suptitle(f"Correlation between {self.x_var} and {self.y_var}")
        canvas = FigureCanvasQTAgg(joint_grid.figure)
        canvas.updateGeometry()
        canvas.draw()
        self.ui.splitter.replaceWidget(0, canvas)

        # Assign canvas to PlotToolbar
        self.plotToolbar.canvas = canvas

        t_test = pg.ttest(df[self.x_var], df[self.y_var])
        corr = pg.pairwise_corr(data=df, columns=[self.x_var, self.y_var], method="pearson")

        html_template = """
            <html>
              <head>
                <title>HTML Pandas Dataframe with CSS</title>
                {style}
              </head>
              <body>
                <h3>t-test</h3>
                {t_test}
                <h3>Pearson correlation</h3>
                {corr}
              </body>
            </html>
            """

        html = html_template.format(
            style=style,
            t_test=t_test.to_html(classes="mystyle"),
            corr=corr.to_html(classes="mystyle"),
        )
        self.ui.webView.setHtml(html)
