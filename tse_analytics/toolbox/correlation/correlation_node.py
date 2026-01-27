from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.pipeline import PipelineNode
from tse_analytics.core.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.core.utils import get_group_by_params
from tse_analytics.toolbox.correlation.processor import get_correlation_result


class CorrelationNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Correlation"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "x_variable",
            "",
            "",
            "X Variable",
            "X variable for correlation",
        )

        self.add_text_input(
            "y_variable",
            "",
            "",
            "Y Variable",
            "Y variable for correlation",
        )

        self.add_combo_menu(
            "group_by",
            "Group by",
            items=[],
            tooltip="Grouping mode",
        )

    def initialize(self, dataset: Dataset, datatable: Datatable):
        # Initialize group_by selector
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

        x_variable = str(self.get_property("x_variable"))
        y_variable = str(self.get_property("y_variable"))
        group_by_str = str(self.get_property("group_by"))

        if not x_variable:
            return PipelinePacket.inactive(reason="No X variable selected")

        if not y_variable:
            return PipelinePacket.inactive(reason="No Y variable selected")

        split_mode, factor_name = get_group_by_params(group_by_str)

        # Determine variable columns (avoid duplicate if same variable)
        variable_columns = [x_variable] if x_variable == y_variable else [x_variable, y_variable]

        # Get dataframe with grouping
        df = datatable.get_df(variable_columns, split_mode, factor_name if factor_name else "")

        # Generate correlation result
        result = get_correlation_result(
            datatable.dataset,
            df,
            x_variable,
            y_variable,
            split_mode,
            factor_name,
            figsize=None,
        )

        return PipelinePacket(datatable, report=result.report)
