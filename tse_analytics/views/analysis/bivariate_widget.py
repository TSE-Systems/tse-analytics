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
from tse_analytics.views.analysis.bivariate_widget_ui import Ui_BivariateWidget
from tse_analytics.views.misc.toast import Toast


class BivariateWidget(QWidget, MessengerListener):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.register_to_messenger(Manager.messenger)

        self.ui = Ui_BivariateWidget()
        self.ui.setupUi(self)

        self.help_path = "bivariate.md"
        self.ui.pushButtonHelp.clicked.connect(lambda: show_help(self, self.help_path))
        self.ui.pushButtonUpdate.clicked.connect(self.__update)

        self.ui.radioButtonCorrelation.toggled.connect(self.__correlation_selected)
        self.ui.radioButtonRegression.toggled.connect(self.__regression_selected)

        self.plot_toolbar = NavigationToolbar2QT(self.ui.canvas, self)
        self.plot_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().insertWidget(0, self.plot_toolbar)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self.__on_dataset_changed)

    def __on_dataset_changed(self, message: DatasetChangedMessage):
        self.ui.pushButtonUpdate.setDisabled(message.data is None)
        self.__clear()
        if message.data is not None:
            self.ui.variableSelectorX.set_data(message.data.variables)
            self.ui.variableSelectorY.set_data(message.data.variables)
            self.ui.factorSelector.set_data(message.data.factors)

    def __clear(self):
        self.ui.variableSelectorX.clear()
        self.ui.variableSelectorY.clear()
        self.ui.factorSelector.clear()
        self.ui.webView.setHtml("")

    def __correlation_selected(self):
        self.ui.groupBoxX.setTitle("X")
        self.ui.groupBoxY.setTitle("Y")

    def __regression_selected(self):
        self.ui.groupBoxX.setTitle("Covariate")
        self.ui.groupBoxY.setTitle("Response")

    def __update(self):
        if self.ui.radioButtonCorrelation.isChecked():
            self.__update_correlation()
        elif self.ui.radioButtonRegression.isChecked():
            self.__update_regression()

    def __update_correlation(self):
        x_var = self.ui.variableSelectorX.currentText()
        y_var = self.ui.variableSelectorY.currentText()

        variables = [x_var] if x_var == y_var else [x_var, y_var]
        df = Manager.data.get_current_df(variables=variables)

        selected_factor = self.ui.factorSelector.currentText()
        if selected_factor != "":
            grouping = selected_factor
        else:
            df["Animal"] = df["Animal"].cat.remove_unused_categories()
            grouping = "Animal"

        joint_grid = sns.jointplot(data=df, x=x_var, y=y_var, hue=grouping)
        joint_grid.fig.suptitle(f"Correlation between {x_var} and {y_var}")
        canvas = FigureCanvasQTAgg(joint_grid.figure)
        canvas.updateGeometry()
        canvas.draw()
        self.ui.splitterVertical.replaceWidget(0, canvas)

        # Assign canvas to PlotToolbar
        new_toolbar = NavigationToolbar2QT(canvas, self)
        new_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().replaceWidget(self.plot_toolbar, new_toolbar)
        self.plot_toolbar.deleteLater()
        self.plot_toolbar = new_toolbar

        t_test = pg.ttest(df[x_var], df[y_var])
        corr = pg.pairwise_corr(data=df, columns=[x_var, y_var], method="pearson")

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

    def __update_regression(self):
        selected_factor = self.ui.factorSelector.currentText()
        if selected_factor == "":
            Toast(text="Please select factor first.", parent=self, duration=2000).show_toast()
            return

        covariate = self.ui.variableSelectorX.currentText()
        response = self.ui.variableSelectorY.currentText()
        hue = selected_factor if selected_factor != "" else "Animal"

        variables = [response] if response == covariate else [response, covariate]
        df = Manager.data.get_current_df(variables=variables)

        df = df.groupby(by=["Animal"], as_index=False).agg({
            covariate: "mean",
            response: "mean",
            selected_factor: "first",
        })

        facet_grid = sns.lmplot(data=df, x=covariate, y=response, hue=hue, robust=False)
        canvas = FigureCanvasQTAgg(facet_grid.figure)

        canvas.updateGeometry()
        canvas.draw()
        self.ui.splitterVertical.replaceWidget(0, canvas)

        # Assign canvas to PlotToolbar
        new_toolbar = NavigationToolbar2QT(canvas, self)
        new_toolbar.setIconSize(QSize(16, 16))
        self.ui.widgetSettings.layout().replaceWidget(self.plot_toolbar, new_toolbar)
        self.plot_toolbar.deleteLater()
        self.plot_toolbar = new_toolbar

        glm = pg.linear_regression(df[[covariate]], df[response])

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
