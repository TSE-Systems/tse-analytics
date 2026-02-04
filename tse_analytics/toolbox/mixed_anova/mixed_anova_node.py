from tse_analytics.core.data.binning import BinningMode
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.enums import EFFECT_SIZE, P_ADJUSTMENT
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.mixed_anova.processor import get_mixed_anova_result


class MixedAnovaNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Mixed-design ANOVA"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "variable",
            "",
            "",
            "Dependent variable",
            "Dependent variable to test",
        )

        self.add_text_input(
            "factor",
            "",
            "",
            "Between-subject factor",
            "Between-subject factor name",
        )

        self.add_combo_menu(
            "effect_size",
            "Effect Size",
            items=list(EFFECT_SIZE.keys()),
            tooltip="Effect size type",
        )

        self.add_combo_menu(
            "p_adjustment",
            "P Adjustment",
            items=list(P_ADJUSTMENT.keys()),
            tooltip="P-value adjustment method",
        )

        self.add_checkbox(
            "do_pairwise_tests",
            "",
            "Pairwise Tests",
            True,
            "Perform pairwise post-hoc tests",
        )

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")

        # Check if binning is applied
        if not datatable.dataset.binning_settings.apply:
            return PipelinePacket.inactive(reason="Please apply a proper binning first")

        # Get configuration properties
        variable_name = str(self.get_property("variable")).strip()
        if not variable_name:
            return PipelinePacket.inactive(reason="No dependent variable specified")

        # Get dependent variable from datatable
        variable = datatable.variables.get(variable_name)
        if variable is None:
            return PipelinePacket.inactive(reason=f"Variable '{variable_name}' not found")

        # Get between-subject factor
        factor_name = str(self.get_property("factor")).strip()
        if not factor_name:
            return PipelinePacket.inactive(reason="No between-subject factor specified")

        # Validate factor exists in dataset
        if factor_name not in datatable.dataset.factors:
            return PipelinePacket.inactive(reason=f"Factor '{factor_name}' not found")

        # Get other settings
        effect_size_label = str(self.get_property("effect_size"))
        p_adjustment_label = str(self.get_property("p_adjustment"))
        do_pairwise_tests = bool(self.get_property("do_pairwise_tests"))

        effect_size = EFFECT_SIZE.get(effect_size_label, "hedges")
        p_adjustment = P_ADJUSTMENT.get(p_adjustment_label, "none")

        # Disable pairwise tests for interval binning by default to avoid long computation
        if datatable.dataset.binning_settings.mode == BinningMode.INTERVALS and do_pairwise_tests:
            # Note: In the widget, this prompts the user. In the node, we just warn via tooltip.
            tooltip = "Warning: Pairwise tests with interval binning may take a long time"
            self.view.setToolTip(tooltip)

        # Get preprocessed dataframe (always use ANIMAL split for Mixed-ANOVA)
        df = datatable.get_preprocessed_df(
            variables={variable.name: variable},
            split_mode=SplitMode.ANIMAL,
            selected_factor_name=None,
            dropna=True,
        )

        # Perform Mixed-ANOVA analysis
        result = get_mixed_anova_result(
            datatable.dataset,
            df,
            variable,
            factor_name,
            do_pairwise_tests,
            effect_size,
            p_adjustment,
            figsize=None,
        )

        return PipelinePacket(datatable, report=result.report)
