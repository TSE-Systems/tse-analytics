from dataclasses import dataclass

import pingouin as pg
from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QComboBox, QInputDialog, QLabel, QToolBar, QVBoxLayout, QWidget
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core import manager
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.report import Report
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_h_spacer_widget, get_html_image_from_figure, get_html_table
from tse_analytics.toolbox.shared import EFFECT_SIZE
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.report_edit import ReportEdit
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

        toolbar.addWidget(QLabel("Effect size type:"))
        self.comboBoxEffectSizeType = QComboBox(toolbar)
        self.comboBoxEffectSizeType.addItems(list(EFFECT_SIZE))
        self.comboBoxEffectSizeType.setCurrentText("Hedges g")
        toolbar.addWidget(self.comboBoxEffectSizeType)

        # Insert toolbar to the widget
        self._layout.addWidget(toolbar)

        self.report_edit = ReportEdit(self)
        self._layout.addWidget(self.report_edit)

        toolbar.addWidget(get_h_spacer_widget(toolbar))
        toolbar.addAction("Add Report").triggered.connect(self._add_report)

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

        # Binning
        df = process_time_interval_binning(
            df,
            TimeIntervalsBinningSettings("day", 365),
            variables,
            origin=self.datatable.dataset.experiment_started,
        )

        # TODO: should or should not?
        df.dropna(inplace=True)

        effsize = EFFECT_SIZE[self.comboBoxEffectSizeType.currentText()]

        normality = pg.normality(df, group=factor_name, dv=dependent_variable_name)
        homoscedasticity = pg.homoscedasticity(df, group=factor_name, dv=dependent_variable_name)

        if homoscedasticity.loc["levene"]["equal_var"]:
            anova = pg.anova(
                data=df,
                dv=dependent_variable_name,
                between=factor_name,
                detailed=True,
            )
            anova_header = "One-way classic ANOVA"

            post_hoc_test = pg.pairwise_tukey(
                data=df,
                dv=dependent_variable_name,
                between=factor_name,
                effsize=effsize,
            )
            post_hoc_test_header = "Pairwise Tukey-HSD post-hoc test"
        else:
            anova = pg.welch_anova(
                data=df,
                dv=dependent_variable_name,
                between=factor_name,
            )
            anova_header = "One-way Welch ANOVA"

            post_hoc_test = pg.pairwise_gameshowell(
                data=df,
                dv=dependent_variable_name,
                between=factor_name,
                effsize=effsize,
            )
            post_hoc_test_header = "Pairwise Games-Howell post-hoc test"

        pairwise_tukeyhsd_res = pairwise_tukeyhsd(df[dependent_variable_name], df[factor_name])
        figure = pairwise_tukeyhsd_res.plot_simultaneous(ylabel="Level", xlabel=dependent_variable_name)
        img_html = get_html_image_from_figure(figure)
        figure.clear()

        html_template = """
                <h2>Factor: {factor_name}</h2>
                {normality}
                {homoscedasticity}
                {anova}
                {post_hoc_test}
                {img_html}
                """

        html = html_template.format(
            factor_name=factor_name,
            anova=get_html_table(anova, anova_header, index=False),
            normality=get_html_table(normality, "Univariate normality test"),
            homoscedasticity=get_html_table(homoscedasticity, "Homoscedasticity (equality of variances)"),
            post_hoc_test=get_html_table(post_hoc_test, post_hoc_test_header, index=False),
            img_html=img_html,
        )
        self.report_edit.set_content(html)

    def _add_report(self):
        name, ok = QInputDialog.getText(
            self,
            "Report",
            "Please enter report name:",
            text=self.title,
        )
        if ok and name:
            manager.add_report(
                Report(
                    self.datatable.dataset,
                    name,
                    self.report_edit.toHtml(),
                )
            )
