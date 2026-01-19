from NodeGraphQt import constants
from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.distribution.processor import get_distribution_result


class DistributionNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Distribution"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "variable",
            "",
            "",
            "Variable",
            "Variable to analyze",
        )

        self.add_combo_menu(
            "group_by",
            "Group by",
            items=[],
            tooltip="Grouping mode",
        )

        self.create_property(
            "plot_type",
            "Violin plot",
            items=["Violin plot", "Box plot"],
            widget_type=constants.NodePropWidgetEnum.QCOMBO_BOX.value,
            widget_tooltip="Plot type",
        )

        self.create_property(
            "show_points",
            False,
            widget_type=constants.NodePropWidgetEnum.QCHECK_BOX.value,
            widget_tooltip="Show data points",
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

        variable_name = str(self.get_property("variable"))
        group_by_str = str(self.get_property("group_by"))
        plot_type = str(self.get_property("plot_type"))
        show_points = bool(self.get_property("show_points"))

        if not variable_name:
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

        # Generate distribution result
        result = get_distribution_result(
            datatable.dataset,
            df,
            variable_name,
            split_mode,
            factor_name,
            plot_type,
            show_points,
            figsize=None,
        )

        return PipelinePacket(datatable, report=result.report)
