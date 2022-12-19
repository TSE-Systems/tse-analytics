from typing import Optional

import pingouin as pg
import seaborn as sns
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_datatools.data.variable import Variable


class GlmWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.help_path = "docs/glm.md"

        self.covariate = ""
        self.covariate_combo_box = VariableSelector()
        self.covariate_combo_box.currentTextChanged.connect(self._covariate_changed)
        self.toolbar.addWidget(QLabel("Covariate: "))
        self.toolbar.addWidget(self.covariate_combo_box)

        self.response = ""
        self.response_combo_box = VariableSelector()
        self.response_combo_box.currentTextChanged.connect(self._response_changed)
        self.toolbar.addWidget(QLabel("Response: "))
        self.toolbar.addWidget(self.response_combo_box)

        self.web_view = QWebEngineView()
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PluginsEnabled, False)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PdfViewerEnabled, False)
        self.web_view.setHtml("")
        self.layout().addWidget(self.web_view)

        self.canvas = None

    def clear(self):
        self.covariate_combo_box.clear()
        self.response_combo_box.clear()
        self.web_view.setHtml("")

    def update_variables(self, variables: dict[str, Variable]):
        covariate_variables = variables.copy()
        covariate_variables["Weight"] = Variable("Weight", "[g]", "Animal weight")
        self.covariate_combo_box.set_data(covariate_variables)
        self.response_combo_box.set_data(variables)

    def _covariate_changed(self, covariate: str):
        self.covariate = covariate

    def _response_changed(self, response: str):
        self.response = response

    def _analyze(self):
        df = Manager.data.selected_dataset.original_df.copy()
        if self.covariate == "Weight":
            df = df.groupby(by=["Animal"], as_index=False).agg({self.response: "mean", "Group": "first"})
        else:
            df = df.groupby(by=["Animal"], as_index=False).agg({self.covariate: "mean", self.response: "mean", "Group": "first"})

        if self.covariate == "Weight":
            df["Weight"] = df["Animal"].astype(float)
            weights = {}
            for animal in Manager.data.selected_dataset.animals.values():
                weights[animal.id] = animal.weight
            df = df.replace({"Weight": weights})

        if self.canvas is not None:
            self.layout().removeWidget(self.canvas)

        facet_grid = sns.lmplot(data=df, x=self.covariate, y=self.response, hue="Group", robust=False)
        self.canvas = FigureCanvasQTAgg(facet_grid.figure)
        self.canvas.updateGeometry()
        self.canvas.draw()
        self.layout().addWidget(self.canvas)

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
        self.web_view.setHtml(html)
