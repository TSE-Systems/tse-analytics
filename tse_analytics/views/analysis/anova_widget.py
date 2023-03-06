from typing import Optional

import pingouin as pg
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QWidget, QSplitter
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_datatools.data.variable import Variable


class AnovaWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.help_path = "docs/anova.md"

        self.variable = ""
        self.variable_selector = VariableSelector()
        self.variable_selector.currentTextChanged.connect(self.__variable_changed)
        self.toolbar.addWidget(QLabel("Variable: "))
        self.toolbar.addWidget(self.variable_selector)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.layout().addWidget(self.splitter)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)
        self.splitter.addWidget(self.canvas)

        self.web_view = QWebEngineView(self)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PluginsEnabled, False)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PdfViewerEnabled, False)
        self.web_view.setHtml("")
        self.splitter.addWidget(self.web_view)

        self.splitter.setSizes([2, 1])

    def clear(self):
        self.variable_selector.clear()
        self.web_view.setHtml("")
        self.ax.clear()

    def update_variables(self, variables: dict[str, Variable]):
        self.variable_selector.set_data(variables)

    def __variable_changed(self, variable: str):
        self.variable = variable

    def _analyze(self):
        if Manager.data.selected_dataset is None or Manager.data.selected_factor is None:
            return

        df = Manager.data.selected_dataset.active_df
        # Drop NaN rows
        # df = df[df["Group"].notna()]
        df = df[df[self.variable].notna()]

        factor_name = Manager.data.selected_factor.name
        homoscedasticity = pg.homoscedasticity(data=df, dv=self.variable, group=factor_name)

        if homoscedasticity["equal_var"].values[0]:
            anova_header = "Classic one-way ANOVA"
            anova = pg.anova(data=df, dv=self.variable, between=factor_name, detailed=True)
        else:
            anova_header = "Welch one-way ANOVA"
            anova = pg.welch_anova(data=df, dv=self.variable, between=factor_name)

        pt = pg.pairwise_tukey(dv=self.variable, between=factor_name, data=df)
        # self.webView.setHtml(pt.to_html())

        tukey = pairwise_tukeyhsd(
            endog=df[self.variable], groups=df[factor_name], alpha=0.05  # Data  # Groups
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
        self.web_view.setHtml(html)

        self.ax.clear()
        tukey.plot_simultaneous(
            ax=self.ax, figsize=self.canvas.figure.get_size_inches()
        )  # Plot group confidence intervals
        self.canvas.figure.tight_layout()
        self.canvas.draw()
