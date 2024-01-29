
import plotly.express as px
from PySide6.QtCore import QDir, QTemporaryFile, QUrl
from PySide6.QtWidgets import QWidget
from tse_datatools.analysis.grouping_mode import GroupingMode

from tse_analytics.core.helper import show_help
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetChangedMessage
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.views.analysis.matrix_widget_ui import Ui_MatrixWidget
from tse_analytics.views.misc.toast import Toast


class MatrixWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_MatrixWidget()
        self.ui.setupUi(self)

        self.help_path = "scatter-matrix.md"
        self.ui.toolButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.toolButtonAnalyse.clicked.connect(self.__analyze)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.toolButtonAnalyse.setDisabled(message.data is None)
        self.__clear()

    def __clear(self):
        self.ui.webView.setHtml("")

    def __analyze(self):
        if len(Manager.data.selected_variables) < 2:
            Toast(text="Please select at least two variables.", parent=self, duration=2000).show_toast()
            return

        if Manager.data.grouping_mode == GroupingMode.FACTORS and Manager.data.selected_factor is None:
            Toast(text="Please select a factor first!", parent=self, duration=2000).show_toast()
            return

        match Manager.data.grouping_mode:
            case GroupingMode.FACTORS:
                color = Manager.data.selected_factor.name
            case GroupingMode.RUNS:
                color = "Run"
            case _:
                color = "Animal"

        variables = [variable.name for variable in Manager.data.selected_variables]
        df = Manager.data.get_current_df(calculate_error=False, variables=variables)

        fig = px.scatter_matrix(df, dimensions=variables, color=color)
        fig.update_traces(diagonal_visible=False)

        file = QTemporaryFile(f"{QDir.tempPath()}/XXXXXX.html", self)
        if file.open():
            fig.write_html(file.fileName(), include_plotlyjs=True)
            self.ui.webView.load(QUrl.fromLocalFile(file.fileName()))
