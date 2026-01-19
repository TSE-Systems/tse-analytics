from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.histogram.processor import get_histogram_result


class HistogramNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Histogram"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "variable",
            "",
            "",
            "Variable",
            "Variable to test",
        )

        self.add_combo_menu(
            "group_by",
            "Group by",
            items=[],
            tooltip="Grouping mode",
        )

    def initialize(self, dataset: Dataset, datatable: Datatable):
        # Initialize variable selector
        if datatable is None:
            variable_names = ["No variables"]
            group_by_options = ["Animal"]
        else:
            variable_names = list(datatable.variables.keys())
            group_by_options = datatable.get_group_by_columns()

        # variable_widget: NodeComboBox = self.get_widget("variable")
        # variable_widget.clear()
        # variable_widget.add_items(variable_names)

        group_by_widget: NodeComboBox = self.get_widget("group_by")
        group_by_widget.clear()
        group_by_widget.add_items(group_by_options)

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")

        variable_name = str(self.get_property("variable"))
        group_by_str = str(self.get_property("group_by"))

        if variable_name == "No variables" or not variable_name:
            return PipelinePacket.inactive(reason="No variable selected")

        # Convert group_by string to SplitMode and factor_name
        match group_by_str:
            case "Animal":
                split_mode = SplitMode.ANIMAL
                factor_name = None
            case "Run":
                split_mode = SplitMode.RUN
                factor_name = None
            case "Total":
                split_mode = SplitMode.TOTAL
                factor_name = None
            case _:
                # Check if it's a factor name
                if group_by_str in datatable.dataset.factors.keys():
                    split_mode = SplitMode.FACTOR
                    factor_name = group_by_str
                else:
                    # Default to Animal if unknown
                    split_mode = SplitMode.ANIMAL
                    factor_name = None

        # Get dataframe with grouping
        df = datatable.get_df([variable_name], split_mode, factor_name if factor_name else "")

        # Generate histogram result
        result = get_histogram_result(
            datatable.dataset,
            df,
            variable_name,
            split_mode,
            factor_name,
            figsize=None,
        )

        return PipelinePacket(datatable, report=result.report)
