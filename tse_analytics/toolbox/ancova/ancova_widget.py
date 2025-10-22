from dataclasses import dataclass

import pingouin as pg
from PySide6.QtCore import QSize, Qt, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QTextEdit
from pyqttoast import ToastPreset
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_h_spacer_widget, get_html_image
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class AncovaWidgetSettings:
    selected_variable: str = None
    selected_covariate: str = None
    selected_factor: str = None


class AncovaWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: AncovaWidgetSettings = settings.value(self.__class__.__name__, AncovaWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "ANCOVA"

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

        toolbar.addWidget(QLabel("Covariate variable:"))
        self.covariate_selector = VariableSelector(toolbar)
        self.covariate_selector.set_data(self.datatable.variables, selected_variable=self._settings.selected_covariate)
        toolbar.addWidget(self.covariate_selector)

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
            AncovaWidgetSettings(
                self.variable_selector.currentText(),
                self.covariate_selector.currentText(),
                self.factor_selector.currentText(),
            ),
        )

    def _update(self):
        dependent_variable = self.variable_selector.get_selected_variable()
        selected_covariate = self.covariate_selector.get_selected_variable()

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
            dependent_variable.name: dependent_variable,
            selected_covariate.name: selected_covariate,
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

        facet_grid = sns.lmplot(
            data=df,
            x=covariate_variable_name,
            y=dependent_variable_name,
            hue=factor_name,
        )
        img_html = get_html_image(facet_grid.figure)
        facet_grid.figure.clear()

        ancova = pg.ancova(
            data=df,
            dv=dependent_variable.name,
            covar=selected_covariate.name,
            between=factor_name,
        ).round(5)

        ancova_model = ols(f"{dependent_variable_name} ~ {covariate_variable_name} + C({factor_name})", data=df).fit()
        ancova_new = anova_lm(ancova_model, typ=2).round(5)
        ancova_full = ancova_model.summary().as_html()

        pairwise_tests = pg.pairwise_tests(
            data=df,
            dv=dependent_variable.name,
            between=factor_name,
            return_desc=True,
        ).round(5)

        covariate_model = ols(f"{dependent_variable_name} ~ {covariate_variable_name}", data=df).fit()
        pairwise_tests_new = pairwise_tukeyhsd(
            endog=covariate_model.resid,
            groups=df[factor_name],
            alpha=0.05,
        ).summary()

        html_template = """
                        <h1>Factor: {factor_name}</h1>
                        <h2>Linearity between Response and Covariate</h2>
                        <p>
                        {img_html}
                        </p>
                        <h2>ANCOVA</h2>
                        {ancova}
                        <h2>ANCOVA (NEW)</h2>
                        {ancova_new}
                        <h2>ANCOVA (NEW FULL)</h2>
                        {ancova_full}
                        <h2>Pairwise post-hoc tests</h2>
                        {pairwise_tests}
                        <h2>Pairwise post-hoc tests (NEW)</h2>
                        {pairwise_tests_new}
                        """

        html = html_template.format(
            img_html=img_html,
            factor_name=factor_name,
            ancova=ancova.to_html(),
            ancova_new=ancova_new.to_html(),
            ancova_full=ancova_full,
            pairwise_tests=pairwise_tests.to_html(),
            pairwise_tests_new=pairwise_tests_new.as_html(),
        )
        self.textEdit.document().setHtml(html)

    def _add_report(self):
        self.datatable.dataset.report += self.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
