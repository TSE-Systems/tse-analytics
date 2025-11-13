from dataclasses import dataclass

import pandas as pd
import pingouin as pg
import seaborn.objects as so
from pyqttoast import ToastPreset
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QMessageBox, QTextEdit, QToolBar, QVBoxLayout, QWidget

from tse_analytics.core import color_manager, messaging
from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.toaster import make_toast
from tse_analytics.core.utils import (
    get_h_spacer_widget,
    get_html_image_from_plot,
    get_html_table,
    get_widget_tool_button,
)
from tse_analytics.styles.css import style_descriptive_table
from tse_analytics.toolbox.rm_anova.rm_anova_settings_widget_ui import Ui_RMAnovaSettingsWidget
from tse_analytics.views.misc.group_by_selector import GroupBySelector
from tse_analytics.views.misc.variable_selector import VariableSelector


@dataclass
class RMAnovaWidgetSettings:
    group_by: str = "Animal"
    selected_variable: str = None


class RMAnovaWidget(QWidget):
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
        self._settings: RMAnovaWidgetSettings = settings.value(self.__class__.__name__, RMAnovaWidgetSettings())

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.title = "Repeated Measures ANOVA"

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

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Group by:"))
        self.group_by_selector = GroupBySelector(
            toolbar,
            self.datatable,
            selected_mode=self._settings.group_by,
            disable_total_mode=True,
        )
        toolbar.addWidget(self.group_by_selector)

        self.settings_widget = QWidget()
        self.settings_widget_ui = Ui_RMAnovaSettingsWidget()
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
            RMAnovaWidgetSettings(
                self.group_by_selector.currentText(),
                self.variable_selector.currentText(),
            ),
        )

    def _update(self):
        split_mode, selected_factor_name = self.group_by_selector.get_group_by()
        variable = self.variable_selector.get_selected_variable()

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
            variables={variable.name: variable},
            split_mode=SplitMode.ANIMAL,
            selected_factor_name=None,
            dropna=True,
        )

        match split_mode:
            case SplitMode.ANIMAL:
                subject = "Animal"
                palette = color_manager.get_animal_to_color_dict(self.datatable.dataset.animals)
            case SplitMode.RUN:
                subject = "Run"
                palette = color_manager.colormap_name
            case SplitMode.FACTOR:
                subject = selected_factor_name
                palette = color_manager.get_level_to_color_dict(self.datatable.dataset.factors[selected_factor_name])
            case _:
                # Disabled for Total grouping mode
                subject = None

        spher, W, chisq, dof, pval = pg.sphericity(
            data=df,
            dv=variable.name,
            within="Bin",
            subject=subject,
            method="mauchly",
        )
        sphericity = pd.DataFrame(
            [[spher, W, chisq, dof, pval]],
            columns=["Sphericity", "W", "Chi-square", "DOF", "p-value"],
        )

        anova = pg.rm_anova(
            data=df,
            dv=variable.name,
            within="Bin",
            subject=subject,
            detailed=True,
        )

        plot = (
            so.Plot(
                df,
                x="Bin",
                y=variable.name,
                color=subject if not split_mode == SplitMode.ANIMAL else None,
            )
            .add(so.Range(), so.Est(errorbar="se"))
            .add(so.Dot(), so.Agg())
            .add(so.Line(), so.Agg())
            .scale(color=palette)
            .label(title=f"{variable.name} over time")
            .layout(size=(10, 5))
        )
        img_html = get_html_image_from_plot(plot)

        html_template = """
                        {img_html}
                        {sphericity}
                        {anova}
                        """

        if do_pairwise_tests:
            effsize = self.eff_size[self.settings_widget_ui.comboBoxEffectSizeType.currentText()]
            padjust = self.p_adjustment[self.settings_widget_ui.comboBoxPAdjustment.currentText()]

            pairwise_tests = pg.pairwise_tests(
                data=df,
                dv=variable.name,
                within="Bin",
                subject=subject,
                return_desc=True,
                effsize=effsize,
                padjust=padjust,
            )

            html_template += """
                            {pairwise_tests}
                            """

            html = html_template.format(
                img_html=img_html,
                sphericity=get_html_table(sphericity, "Sphericity Test", index=False),
                anova=get_html_table(anova, "Repeated measures one-way ANOVA", index=False),
                pairwise_tests=get_html_table(pairwise_tests, "Pairwise post-hoc tests", index=False),
            )
        else:
            html = html_template.format(
                img_html=img_html,
                sphericity=get_html_table(sphericity, "Sphericity Test", index=False),
                anova=get_html_table(anova, "Repeated measures one-way ANOVA", index=False),
            )

        self.textEdit.document().setHtml(html)

    def _add_report(self):
        self.datatable.dataset.report += self.textEdit.toHtml()
        messaging.broadcast(messaging.AddToReportMessage(self, self.datatable.dataset))
