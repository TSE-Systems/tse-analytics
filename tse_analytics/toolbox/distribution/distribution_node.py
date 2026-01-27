from NodeGraphQt import constants
from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.pipeline import PipelineNode
from tse_analytics.core.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.core.utils import get_group_by_params
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

        split_mode, factor_name = get_group_by_params(group_by_str)

        # Get dataframe with grouping
        df = datatable.get_df([variable_name], split_mode, factor_name)

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
