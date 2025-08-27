import pingouin as pg
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QTextEdit, QComboBox
from pyqttoast import ToastPreset
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.core.toaster import make_toast
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class OneWayAnovaWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "One-way ANOVA"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Data Plot Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("Dependent variable:"))
        self.variable_selector = VariableSelector(toolbar)
        self.variable_selector.set_data(self.datatable.variables)
        toolbar.addWidget(self.variable_selector)

        toolbar.addWidget(QLabel("Factor:"))
        self.factor_selector = FactorSelector(toolbar)
        self.factor_selector.set_data(self.datatable.dataset.factors, add_empty_item=False)
        toolbar.addWidget(self.factor_selector)

        self.eff_size = {
            "No effect size": "none",
            "Unbiased Cohen d": "cohen",
            "Hedges g": "hedges",
            # "Pearson correlation coefficient": "r",
            "Eta-square": "eta-square",
            "Odds ratio": "odds-ratio",
            "Area Under the Curve": "AUC",
            "Common Language Effect Size": "CLES",
        }
        toolbar.addWidget(QLabel("Effect size type:"))
        self.comboBoxEffectSizeType = QComboBox(toolbar)
        self.comboBoxEffectSizeType.addItems(self.eff_size.keys())
        self.comboBoxEffectSizeType.setCurrentText("Hedges g")
        toolbar.addWidget(self.comboBoxEffectSizeType)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.textEdit = QTextEdit(
            toolbar,
            undoRedoEnabled=False,
            readOnly=True,
            lineWrapMode=QTextEdit.LineWrapMode.NoWrap,
        )
        self.textEdit.document().setDefaultStyleSheet(style_descriptive_table)
        self._layout.addWidget(self.textEdit)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add to Report").triggered.connect(self._add_report)

    def _update(self):
        dependent_variable = self.variable_selector.get_selected_variable()
        if dependent_variable is None:
            make_toast(
                self,
                self.title,
                "Please select dependent variable.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        dependent_variable_name = dependent_variable.name

        factor_name = self.factor_selector.currentText()
        if factor_name == "":
            make_toast(
                self,
                self.title,
                "Please select a single factor.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        variables = {
            dependent_variable_name: dependent_variable,
        }

        columns = self.datatable.get_default_columns() + list(self.datatable.dataset.factors) + list(variables)
        df = self.datatable.get_filtered_df(columns)

        # Binning
        df = process_time_interval_binning(
            df,
            TimeIntervalsBinningSettings("day", 365),
            variables,
            origin=self.datatable.dataset.experiment_started,
        )

        # TODO: should or should not?
        df.dropna(inplace=True)

        effsize = self.eff_size[self.comboBoxEffectSizeType.currentText()]

        normality = pg.normality(df, group=factor_name, dv=dependent_variable_name).round(5)
        homoscedasticity = pg.homoscedasticity(df, group=factor_name, dv=dependent_variable_name).round(5)

        if homoscedasticity.loc["levene"]["equal_var"]:
            anova = pg.anova(
                data=df,
                dv=dependent_variable_name,
                between=factor_name,
                detailed=True,
            ).round(5)
            anova_header = "One-way classic ANOVA"

            post_hoc_test = pg.pairwise_tukey(
                data=df,
                dv=dependent_variable_name,
                between=factor_name,
                effsize=effsize,
            ).round(5)
            post_hoc_test_header = "Pairwise Tukey-HSD post-hoc test"
        else:
            anova = pg.welch_anova(
                data=df,
                dv=dependent_variable_name,
                between=factor_name,
            ).round(5)
            anova_header = "One-way Welch ANOVA"

            post_hoc_test = pg.pairwise_gameshowell(
                data=df,
                dv=dependent_variable_name,
                between=factor_name,
                effsize=effsize,
            ).round(5)
            post_hoc_test_header = "Pairwise Games-Howell post-hoc test"

        pairwise_tukeyhsd_res = pairwise_tukeyhsd(df[dependent_variable_name], df[factor_name])
        fig = pairwise_tukeyhsd_res.plot_simultaneous(ylabel="Level", xlabel=dependent_variable_name)
        img_html = get_html_image(fig)
        fig.clear()

        html_template = """
                <h1>Factor: {factor_name}</h1>
                <h2>Univariate normality test</h2>
                {normality}
                <h2>Homoscedasticity (equality of variances)</h2>
                {homoscedasticity}
                <h2>{anova_header}</h2>
                {anova}
                <h2>{post_hoc_test_header}</h2>
                {post_hoc_test}
                {img_html}
                """

        html = html_template.format(
            factor_name=factor_name,
            anova=anova.to_html(index=False),
            anova_header=anova_header,
            normality=normality.to_html(),
            homoscedasticity=homoscedasticity.to_html(),
            post_hoc_test=post_hoc_test.to_html(index=False),
            post_hoc_test_header=post_hoc_test_header,
            img_html=img_html,
        )
        self.textEdit.document().setHtml(html)

    def _add_report(self):
        self.datatable.dataset.report += self.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
