import pandas as pd
import pingouin as pg
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QToolBar, QLabel, QTextEdit, QVBoxLayout, QComboBox
from pyqttoast import ToastPreset
from statsmodels.stats.anova import AnovaRM

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import get_h_spacer_widget
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.toolbox.rm_anova.processor import mauchly_test, repeated_measures_anova_posthoc
from tse_analytics.views.misc.variable_selector import VariableSelector


class RMAnovaWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Repeated Measures ANOVA"

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

        self.p_adjustment = {
            "No correction": "none",
            "Bonferroni": "bonf",
            "Holm": "holm",
        }
        toolbar.addWidget(QLabel("P-values adjustment:"))
        self.p_adjustment_combobox = QComboBox(toolbar)
        self.p_adjustment_combobox.addItems(self.p_adjustment.keys())
        self.p_adjustment_combobox.setCurrentText("No correction")
        toolbar.addWidget(self.p_adjustment_combobox)

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

        df = self.datatable.get_preprocessed_df(
            variables={dependent_variable: selected_dependent_variable},
            split_mode=SplitMode.ANIMAL,
            selected_factor_name=None,
            dropna=True,
        )

        spher, W, chisq, dof, pval = pg.sphericity(
            data=df,
            dv=dependent_variable,
            within="Bin",
            subject="Animal",
            method="mauchly",
        )
        sphericity = pd.DataFrame(
            [[spher, W, chisq, dof, pval]],
            columns=["Sphericity", "W", "Chi-square", "DOF", "p-value"],
        ).round(5)

        sphericity_new = mauchly_test(df, dependent_variable, "Bin", "Animal").to_frame().round(5)

        anova = pg.rm_anova(
            data=df,
            dv=dependent_variable,
            within="Bin",
            subject="Animal",
            detailed=True,
        ).round(5)

        aov = AnovaRM(df, depvar=dependent_variable, subject="Animal", within=["Bin"])
        anova_new = aov.fit().summary().as_html()

        padjust = self.p_adjustment[self.p_adjustment_combobox.currentText()]

        post_hoc_test = pg.pairwise_tests(
            data=df,
            dv=dependent_variable,
            within="Bin",
            subject="Animal",
            return_desc=True,
            padjust=padjust,
        ).round(5)

        post_hoc_test_new = pd.DataFrame(
            repeated_measures_anova_posthoc(
                df,
                "Bin",
                dependent_variable,
                alpha=0.05,
                method=padjust,
            )
        ).round(5)

        html_template = """
        <h2>Sphericity test</h2>
        {sphericity}
        <h2>Sphericity test (NEW)</h2>
        {sphericity_new}
        <h2>Repeated measures one-way ANOVA</h2>
        {anova}
        <h2>Repeated measures one-way ANOVA (NEW)</h2>
        {anova_new}
        <h2>Post-hoc test</h2>
        {post_hoc_test}
        <h2>Post-hoc test (NEW)</h2>
        {post_hoc_test_new}
        """

        html = html_template.format(
            sphericity=sphericity.to_html(),
            sphericity_new=sphericity_new.to_html(),
            anova=anova.to_html(),
            anova_new=anova_new,
            post_hoc_test=post_hoc_test.to_html(),
            post_hoc_test_new=post_hoc_test_new.to_html(),
        )

        self.textEdit.document().setHtml(html)

    def _add_report(self):
        self.datatable.dataset.report += self.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
