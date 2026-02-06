from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_group_by_params
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.mds.processor import get_mds_result


class MdsNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "MDS"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "variables",
            "",
            "",
            "Variables",
            "Comma-separated variable names",
        )

        self.add_combo_menu(
            "group_by",
            "Group by",
            items=[],
            tooltip="Grouping mode",
        )

        self.add_text_input(
            "max_iterations",
            "Max Iterations",
            "300",
            "Max Iterations",
            "Maximum iterations (100-1000)",
        )

    def initialize(self, dataset: Dataset, datatable: Datatable):
        if datatable is None:
            group_by_options = ["Animal"]
        else:
            group_by_options = datatable.get_group_by_columns()

        group_by_widget: NodeComboBox = self.get_widget("group_by")
        group_by_widget.clear()
        group_by_widget.add_items(group_by_options)

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")

        # Parse variables
        variables_raw = str(self.get_property("variables")).strip()
        if not variables_raw:
            return PipelinePacket.inactive(reason="No variables selected")

        variable_names = [name.strip() for name in variables_raw.replace(";", ",").split(",") if name.strip()]
        variable_names = list(dict.fromkeys(variable_names))
        if len(variable_names) < 3:
            return PipelinePacket.inactive(reason="Select at least three variables")

        invalid_variables = [name for name in variable_names if name not in datatable.variables]
        if invalid_variables:
            invalid = ", ".join(invalid_variables)
            return PipelinePacket.inactive(reason=f"Invalid variable(s): {invalid}")

        # Parse group_by
        group_by_str = str(self.get_property("group_by"))
        split_mode, factor_name = get_group_by_params(group_by_str)
        if split_mode == SplitMode.FACTOR:
            if not factor_name:
                return PipelinePacket.inactive(reason="No factor selected")
            if factor_name not in datatable.dataset.factors:
                return PipelinePacket.inactive(reason="Invalid factor selected")

        # Parse max_iterations
        try:
            max_iterations = int(self.get_property("max_iterations"))
            if max_iterations < 100 or max_iterations > 1000:
                return PipelinePacket.inactive(reason="Max iterations must be between 100 and 1000")
        except ValueError, TypeError:
            return PipelinePacket.inactive(reason="Invalid max iterations value")

        # Get data
        df = datatable.get_df(
            variable_names,
            split_mode,
            factor_name,
        )
        df.dropna(inplace=True)

        # Perform MDS analysis
        result = get_mds_result(
            datatable.dataset,
            df,
            variable_names,
            split_mode,
            factor_name,
            max_iterations,
        )

        return PipelinePacket(datatable, report=result.report)
