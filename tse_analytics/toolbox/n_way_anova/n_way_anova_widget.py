from dataclasses import dataclass, field

import pingouin as pg
from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QAbstractItemView, QAbstractScrollArea, QLabel, QTextEdit, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_h_spacer_widget, get_html_table, get_widget_tool_button
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.toolbox.n_way_anova.n_way_anova_settings_widget_ui import Ui_NWayAnovaSettingsWidget
from tse_analytics.views.misc.factors_table_widget import FactorsTableWidget
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class NWayAnovaWidgetSettings:
    selected_variable: str = None
    selected_factors: list[str] = field(default_factory=list)


class NWayAnovaWidget(QWidget):
    p_adjustment = {
        "No correction": "none",
        "One-step Bonferroni": "bonf",
        "One-step Sidak": "sidak",
        "Step-down Bonferroni": "holm",
        "Benjamini/Hochberg FDR": "fdr_bh",
        "Benjamini/Yekutieli FDR": "fdr_by",
    }

    eff_size = {
        "No effect size": "none",
        "Unbiased Cohen d": "cohen",
        "Hedges g": "hedges",
        # "Pearson correlation coefficient": "r",
        "Eta-square": "eta-square",
        "Odds ratio": "odds-ratio",
        "Area Under the Curve": "AUC",
        "Common Language Effect Size": "CLES",
    }

    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        # Connect destructor to unsubscribe and save settings
        self.destroyed.connect(lambda: self._destroyed())

        # Settings management
        settings = QSettings()
        self._settings: NWayAnovaWidgetSettings = settings.value(self.__class__.__name__, NWayAnovaWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "N-way ANOVA"

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

        self.factors_table_widget = FactorsTableWidget()
        self.factors_table_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.factors_table_widget.set_data(
            self.datatable.dataset.factors, selected_factors=self._settings.selected_factors
        )
        self.factors_table_widget.setMaximumHeight(400)
        self.factors_table_widget.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        factors_button = get_widget_tool_button(
            toolbar,
            self.factors_table_widget,
            "Factors",
            QIcon(":/icons/factors.png"),
        )
        toolbar.addWidget(factors_button)

        self.settings_widget = QWidget()
        self.settings_widget_ui = Ui_NWayAnovaSettingsWidget()
        self.settings_widget_ui.setupUi(self.settings_widget)
        settings_button = get_widget_tool_button(
            toolbar,
            self.settings_widget,
            "Settings",
            QIcon(":/icons/icons8-settings-16.png"),
        )
        toolbar.addWidget(settings_button)

        self.settings_widget_ui.comboBoxPAdjustment.addItems(self.p_adjustment.keys())
        self.settings_widget_ui.comboBoxPAdjustment.setCurrentText("No correction")

        self.settings_widget_ui.comboBoxEffectSizeType.addItems(self.eff_size.keys())
        self.settings_widget_ui.comboBoxEffectSizeType.setCurrentText("Hedges g")

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
            NWayAnovaWidgetSettings(
                self.variable_selector.currentText(),
                self.factors_table_widget.get_selected_factor_names(),
            ),
        )

    def _update(self):
        selected_dependent_variable = self.variable_selector.get_selected_variable()
        if selected_dependent_variable is None:
            make_toast(
                self,
                self.title,
                "Please select dependent variable.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        dependent_variable = selected_dependent_variable.name
        factor_names = self.factors_table_widget.get_selected_factor_names()

        match len(factor_names):
            case 2:
                anova_header = "Two-way ANOVA"
            case 3:
                anova_header = "Three-way ANOVA"
            case _:
                anova_header = "Multi-way ANOVA"

        if len(factor_names) < 2:
            make_toast(
                self,
                anova_header,
                "Please select several factors.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return

        variables = {
            dependent_variable: selected_dependent_variable,
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

        # Sanitize variable name: comma, bracket, and colon are not allowed in column names
        sanitized_dependent_variable = dependent_variable.replace("(", "_").replace(")", "").replace(",", "_")
        if sanitized_dependent_variable != dependent_variable:
            df.rename(columns={dependent_variable: sanitized_dependent_variable}, inplace=True)
            dependent_variable = sanitized_dependent_variable

        anova = pg.anova(
            data=df,
            dv=dependent_variable,
            between=factor_names,
            detailed=True,
        )

        effsize = self.eff_size[self.settings_widget_ui.comboBoxEffectSizeType.currentText()]
        padjust = self.p_adjustment[self.settings_widget_ui.comboBoxPAdjustment.currentText()]

        html_template = """
                        {anova}
                        """

        if len(factor_names) > 2:
            html = html_template.format(
                anova=get_html_table(anova, anova_header, index=False),
            )
        else:
            post_hoc_test = pg.pairwise_tests(
                data=df,
                dv=dependent_variable,
                between=factor_names,
                return_desc=True,
                effsize=effsize,
                padjust=padjust,
                nan_policy="listwise",
            )

            html_template += """
                            {post_hoc_test}
                            """

            html = html_template.format(
                anova=get_html_table(anova, anova_header, index=False),
                post_hoc_test=get_html_table(post_hoc_test, "Pairwise post-hoc tests", index=False),
            )

        self.textEdit.document().setHtml(html)

    def _add_report(self):
        self.datatable.dataset.report += self.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
