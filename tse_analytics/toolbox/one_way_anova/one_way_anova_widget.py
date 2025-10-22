import pandas as pd
import scikit_posthocs as sp
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QTextEdit
from pyqttoast import ToastPreset
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.oneway import anova_oneway

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_html_image, get_h_spacer_widget
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.toolbox.one_way_anova.processor import normality_test, homoscedasticity_test
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class OneWayAnovaWidgetSettings:
    selected_variable: str = None
    selected_factor: str = None


class OneWayAnovaWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: OneWayAnovaWidgetSettings = settings.value(self.__class__.__name__, OneWayAnovaWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "One-way ANOVA"

        self.datatable = datatable

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )

        toolbar.addAction(QIcon(":/icons/icons8-refresh-16.png"), "Update").triggered.connect(self._update)
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("Dependent variable:"))
        self.variable_selector = VariableSelector(toolbar)
        self.variable_selector.set_data(self.datatable.variables, selected_variable=self._settings.selected_variable)
        toolbar.addWidget(self.variable_selector)

        toolbar.addWidget(QLabel("Factor:"))
        self.factor_selector = FactorSelector(toolbar)
        self.factor_selector.set_data(self.datatable.dataset.factors, selected_factor=self._settings.selected_factor)
        toolbar.addWidget(self.factor_selector)

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

    def _destroyed(self):
        settings = QSettings()
        settings.setValue(
            self.__class__.__name__,
            OneWayAnovaWidgetSettings(
                self.variable_selector.currentText(),
                self.factor_selector.currentText(),
            ),
        )

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

        # Group by animal
        df = process_time_interval_binning(
            df,
            TimeIntervalsBinningSettings("day", 365),
            variables,
            origin=self.datatable.dataset.experiment_started,
        )

        # TODO: should or should not?
        df.dropna(inplace=True)

        normality = normality_test(df, dependent_variable_name, factor_name).round(5)
        homoscedasticity = homoscedasticity_test(df, dependent_variable_name, factor_name).round(5)

        equal_var = homoscedasticity.iloc[0]["equal"]
        if equal_var:
            anova_result = anova_oneway(
                df[dependent_variable_name], df[factor_name], use_var="equal", welch_correction=False
            )
            anova = pd.DataFrame([
                {
                    "F": anova_result.statistic,
                    "p-value": anova_result.pvalue,
                    "DoF": anova_result.df_num,
                }
            ]).round(5)
            anova_header = "One-way standard ANOVA"

            post_hoc_test = sp.posthoc_tukey(
                df,
                val_col=dependent_variable_name,
                group_col=factor_name,
            ).round(5)
            post_hoc_test_header = "Pairwise Tukey's post-hoc test"
        else:
            anova_result = anova_oneway(
                df[dependent_variable_name],
                df[factor_name],
                use_var="unequal",
                welch_correction=True,
            )
            anova = pd.DataFrame([
                {
                    "F": anova_result.statistic,
                    "p-value": anova_result.pvalue,
                    "DoF": anova_result.df_num,
                }
            ]).round(5)
            anova_header = "One-way Welch ANOVA"

            post_hoc_test = sp.posthoc_tamhane(
                df,
                val_col=dependent_variable_name,
                group_col=factor_name,
                welch=False,
            ).round(5)
            post_hoc_test_header = "Pairwise Tamhane's T2 post-hoc test"

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
            anova=anova.to_html(),
            anova_header=anova_header,
            normality=normality.to_html(),
            homoscedasticity=homoscedasticity.to_html(index=False),
            post_hoc_test=post_hoc_test.to_html(),
            post_hoc_test_header=post_hoc_test_header,
            img_html=img_html,
        )
        self.textEdit.document().setHtml(html)

    def _add_report(self):
        self.datatable.dataset.report += self.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
