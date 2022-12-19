from typing import Optional

import pandas as pd
import pingouin as pg
import seaborn as sns
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QWidget, QSplitter

from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_datatools.data.variable import Variable

pd.set_option("colheader_justify", "center")  # FOR TABLE <th>
sns.set_theme(style="whitegrid")


class CorrelationWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.help_path = "docs/correlation.md"

        self.x_var = ""
        self.x_combo_box = VariableSelector()
        self.x_combo_box.currentTextChanged.connect(self._x_current_text_changed)
        self.toolbar.addWidget(QLabel("X: "))
        self.toolbar.addWidget(self.x_combo_box)

        self.y_var = ""
        self.y_combo_box = VariableSelector()
        self.y_combo_box.currentTextChanged.connect(self._y_current_text_changed)
        self.toolbar.addWidget(QLabel("Y: "))
        self.toolbar.addWidget(self.y_combo_box)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.layout().addWidget(self.splitter)

        self.splitter.addWidget(FigureCanvasQTAgg(None))

        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PluginsEnabled, False)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PdfViewerEnabled, False)
        self.web_view.setHtml("")
        self.splitter.addWidget(self.web_view)

        self.splitter.setSizes([2, 1])

    def update_variables(self, variables: dict[str, Variable]):
        self.x_combo_box.set_data(variables)
        self.y_combo_box.set_data(variables)

    def _analyze(self):
        if len(Manager.data.selected_dataset.groups) == 0:
            return

        df = Manager.data.selected_dataset.original_df

        multivariate_normality = pg.multivariate_normality(df[[self.x_var, self.y_var]])
        corr = pg.pairwise_corr(data=df, columns=[self.x_var, self.y_var], method="pearson")

        joint_grid = sns.jointplot(data=df, x=self.x_var, y=self.y_var, hue="Group")
        canvas = FigureCanvasQTAgg(joint_grid.figure)
        canvas.updateGeometry()
        canvas.draw()
        self.splitter.replaceWidget(0, canvas)

        html_template = """
                <html>
                  <head>
                    <title>HTML Pandas Dataframe with CSS</title>
                    {style}
                  </head>
                  <body>
                    <h3>Test for bivariate normality (Henze-Zirkler)</h3>
                    {multivariate_normality}
                    <h3>Pearson correlation</h3>
                    {corr}
                  </body>
                </html>
                """

        html = html_template.format(
            style=style,
            multivariate_normality=multivariate_normality,
            corr=corr.to_html(classes="mystyle"),
        )
        self.web_view.setHtml(html)

    def clear(self):
        self.x_combo_box.clear()
        self.y_combo_box.clear()
        self.web_view.setHtml("")

    def _x_current_text_changed(self, x: str):
        self.x_var = x

    def _y_current_text_changed(self, y: str):
        self.y_var = y
