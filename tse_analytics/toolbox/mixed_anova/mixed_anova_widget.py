import pandas as pd
import pingouin as pg
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QToolBar, QLabel, QTextEdit
from pyqttoast import ToastPreset

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_widget_tool_button, get_h_spacer_widget
from tse_analytics.core.toaster import make_toast
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.toolbox.mixed_anova.mixed_anova_settings_widget_ui import Ui_MixedAnovaSettingsWidget
from tse_analytics.toolbox.mixed_anova.processor import mixed_anova_manual, posthoc_tests
from tse_analytics.toolbox.rm_anova.processor import mauchly_test
from tse_analytics.views.misc.factor_selector import FactorSelector
from tse_analytics.views.misc.variable_selector import VariableSelector


class MixedAnovaWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Mixed-design ANOVA"

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

        self.settings_widget = QWidget()
        self.settings_widget_ui = Ui_MixedAnovaSettingsWidget()
        self.settings_widget_ui.setupUi(self.settings_widget)
        settings_button = get_widget_tool_button(
            toolbar,
            self.settings_widget,
            "Settings",
            QIcon(":/icons/icons8-settings-16.png"),
        )
        toolbar.addWidget(settings_button)

        self.p_adjustment = {
            "No correction": "none",
            "One-step Bonferroni": "bonf",
            "One-step Sidak": "sidak",
            "Step-down Bonferroni": "holm",
            "Benjamini/Hochberg FDR": "fdr_bh",
            "Benjamini/Yekutieli FDR": "fdr_by",
        }
        self.settings_widget_ui.comboBoxPAdjustment.addItems(self.p_adjustment.keys())
        self.settings_widget_ui.comboBoxPAdjustment.setCurrentText("No correction")

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

        do_pairwise_tests = True
        if not self.datatable.dataset.binning_settings.apply:
            make_toast(
                self,
                self.title,
                "Please apply a proper binning first.",
                duration=2000,
                preset=ToastPreset.WARNING,
                show_duration_bar=True,
            ).show()
            return
        elif self.datatable.dataset.binning_settings.mode == BinningMode.INTERVALS:
            if (
                QMessageBox.question(
                    self,
                    "Perform pairwise tests?",
                    "Calculation of pairwise tests with many time bins can take a long time!",
                )
                == QMessageBox.StandardButton.No
            ):
                do_pairwise_tests = False

        df = self.datatable.get_preprocessed_df(
            variables={dependent_variable_name: dependent_variable},
            split_mode=SplitMode.ANIMAL,
            selected_factor_name=None,
            dropna=True,
        )

        anova = pg.mixed_anova(
            data=df,
            dv=dependent_variable_name,
            between=factor_name,
            within="Bin",
            subject="Animal",
        ).round(5)

        anova_new = mixed_anova_manual(df, 'Animal', factor_name, 'Bin', dependent_variable_name).round(5)

        spher, W, chisq, dof, pval = pg.sphericity(
            data=df,
            dv=dependent_variable_name,
            within="Bin",
            subject="Animal",
            method="mauchly",
        )
        sphericity = pd.DataFrame(
            [[spher, W, chisq, dof, pval]],
            columns=["Sphericity", "W", "Chi-square", "DOF", "p-value"],
        ).round(5)

        sphericity_new = mauchly_test(df, dependent_variable_name, "Bin", "Animal").to_frame().round(5)

        if do_pairwise_tests:
            effsize = self.eff_size[self.settings_widget_ui.comboBoxEffectSizeType.currentText()]
            padjust = self.p_adjustment[self.settings_widget_ui.comboBoxPAdjustment.currentText()]

            pairwise_tests = pg.pairwise_tests(
                data=df,
                dv=dependent_variable_name,
                within="Bin",
                between=factor_name,
                subject="Animal",
                return_desc=True,
                effsize=effsize,
                padjust=padjust,
            ).round(5)

            html_template = """
                                        <h2>Sphericity test</h2>
                                        {sphericity}
                                        <h2>Sphericity test (NEW)</h2>
                                        {sphericity_new}
                                        <h2>Mixed-design ANOVA</h2>
                                        {anova}
                                        <h2>Mixed-design ANOVA (NEW)</h2>
                                        {anova_new}
                                        <h2>Pairwise post-hoc tests</h2>
                                        {pairwise_tests}
                                        """

            html = html_template.format(
                sphericity=sphericity.to_html(),
                sphericity_new=sphericity_new.to_html(),
                anova=anova.to_html(),
                anova_new=anova_new.to_html(),
                pairwise_tests=pairwise_tests.to_html(),
            )
        else:
            html_template = """
                                        <h2>Sphericity test</h2>
                                        {sphericity}
                                        <h2>Mixed-design ANOVA</h2>
                                        {anova}
                                        """

            html = html_template.format(
                sphericity=sphericity.to_html(),
                anova=anova.to_html(),
            )

        self.textEdit.document().setHtml(html)

    def _add_report(self):
        self.datatable.dataset.report += self.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
