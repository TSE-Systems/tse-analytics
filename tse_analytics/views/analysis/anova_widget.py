from typing import Optional

import pandas as pd
import pingouin as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core.manager import Manager
from tse_analytics.css import style


class AnovaWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        description_widget = QTextEdit(
            "The output of the Tukey test shows the average difference, a confidence interval as well as whether you should reject the null hypothesis for each pair of groups at the given significance level. In this case, the test suggests we reject the null hypothesis for 3 pairs, with each pair including the ""white"" category. This suggests the white group is likely different from the others. The 95% confidence interval plot reinforces the results visually: only 1 other group's confidence interval overlaps the white group's confidence interval.")
        description_widget.setFixedHeight(100)
        description_widget.setReadOnly(True)
        self.layout.addWidget(description_widget)

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout.addWidget(self.webView)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)
        self.layout.addWidget(self.canvas)

    def analyze(self, df: pd.DataFrame, variable: str):
        if len(Manager.data.selected_groups) == 0:
            return

        homoscedasticity = pg.homoscedasticity(data=df, dv=variable, group="Group")

        if homoscedasticity["equal_var"].values[0]:
            anova_header = "Classic one-way ANOVA"
            anova = pg.anova(data=df, dv=variable, between="Group", detailed=True)
        else:
            anova_header = "Welch one-way ANOVA"
            anova = pg.welch_anova(data=df, dv=variable, between="Group")

        pt = pg.pairwise_tukey(dv=variable, between='Group', data=df)
        # self.webView.setHtml(pt.to_html())

        tukey = pairwise_tukeyhsd(endog=df[variable],  # Data
                                  groups=df["Group"],  # Groups
                                  alpha=0.05)  # Significance level

        html_template = '''
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
        '''

        html = html_template.format(
            style=style,
            homoscedasticity=homoscedasticity.to_html(classes='mystyle'),
            anova_header=anova_header,
            anova=anova.to_html(classes='mystyle'),
            tukey=pt.to_html(classes='mystyle'),
        )
        self.webView.setHtml(html)

        self.ax.clear()
        tukey.plot_simultaneous(ax=self.ax,
                                figsize=self.canvas.figure.get_size_inches())  # Plot group confidence intervals
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        self.webView.setHtml("")
        self.ax.clear()
