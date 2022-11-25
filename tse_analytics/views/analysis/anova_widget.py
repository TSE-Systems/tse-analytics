from typing import Optional

import pingouin as pg
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QToolBar, QLabel, QComboBox
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core.manager import Manager
from tse_analytics.css import style
from tse_datatools.data.variable import Variable


class AnovaWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.variable_combo_box = QComboBox(self)
        self.variable = ''

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self._get_toolbar())

        description_widget = QTextEdit(
            "The output of the Tukey test shows the average difference, a confidence interval as well as whether you should reject the null hypothesis for each pair of groups at the given significance level. In this case, the test suggests we reject the null hypothesis for 3 pairs, with each pair including the ""white"" category. This suggests the white group is likely different from the others. The 95% confidence interval plot reinforces the results visually: only 1 other group's confidence interval overlaps the white group's confidence interval.")
        description_widget.setFixedHeight(100)
        description_widget.setReadOnly(True)
        self.layout.addWidget(description_widget)

        self.webView = QWebEngineView(self)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, False)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, False)
        self.webView.setHtml('')
        self.layout.addWidget(self.webView)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.ax = figure.subplots()
        self.canvas = FigureCanvasQTAgg(figure)
        self.layout.addWidget(self.canvas)

    def clear(self):
        self.webView.setHtml("")
        self.ax.clear()

    def update_variables(self, variables: dict[str, Variable]):
        self.variable = ''
        self.variable_combo_box.clear()
        self.variable_combo_box.addItems(variables)
        self.variable_combo_box.setCurrentText(self.variable)

    def _variable_changed(self, variable: str):
        self.variable = variable

    def _analyze(self):
        if Manager.data.selected_dataset is None:
            return

        df = Manager.data.selected_dataset.original_df

        homoscedasticity = pg.homoscedasticity(data=df, dv=self.variable, group="Group")

        if homoscedasticity["equal_var"].values[0]:
            anova_header = "Classic one-way ANOVA"
            anova = pg.anova(data=df, dv=self.variable, between="Group", detailed=True)
        else:
            anova_header = "Welch one-way ANOVA"
            anova = pg.welch_anova(data=df, dv=self.variable, between="Group")

        pt = pg.pairwise_tukey(dv=self.variable, between='Group', data=df)
        # self.webView.setHtml(pt.to_html())

        tukey = pairwise_tukeyhsd(endog=df[self.variable],  # Data
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



    def _get_toolbar(self) -> QToolBar:
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        label = QLabel("Variable: ")
        toolbar.addWidget(label)

        self.variable_combo_box.currentTextChanged.connect(self._variable_changed)
        toolbar.addWidget(self.variable_combo_box)

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self._analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
