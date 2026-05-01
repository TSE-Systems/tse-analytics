from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.regression.processor import get_regression_result


class RegressionNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Regression"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "covariate_variable",
            "",
            "",
            "Covariate",
            "Covariate variable for regression",
        )

        self.add_text_input(
            "response_variable",
            "",
            "",
            "Response",
            "Response variable for regression",
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

        covariate_name = str(self.get_property("covariate_variable"))
        response_name = str(self.get_property("response_variable"))
        factor_name = str(self.get_property("group_by"))

        if not covariate_name:
            return PipelinePacket.inactive(reason="No covariate variable selected")

        if not response_name:
            return PipelinePacket.inactive(reason="No response variable selected")

        covariate = datatable.variables.get(covariate_name)
        if covariate is None:
            return PipelinePacket.inactive(reason="Invalid covariate variable")

        response = datatable.variables.get(response_name)
        if response is None:
            return PipelinePacket.inactive(reason="Invalid response variable")

        result = get_regression_result(
            datatable,
            covariate,
            response,
            factor_name,
            figsize=None,
        )

        return PipelinePacket(datatable, report=result.report)
