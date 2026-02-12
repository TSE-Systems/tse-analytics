from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.core.utils import get_group_by_params
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.data_plot.processor import ERROR_BAR_TYPE, get_data_plot_result


class DataPlotNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "DataPlot"

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

        self.add_combo_menu(
            "error_bar",
            "Error Bar",
            items=list(ERROR_BAR_TYPE.keys()),
            tooltip="Error bar type",
        )
        self.set_property("error_bar", "Standard Error")

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

        variables_raw = str(self.get_property("variables")).strip()
        if not variables_raw:
            return PipelinePacket.inactive(reason="No variables selected")

        variable_names = [name.strip() for name in variables_raw.replace(";", ",").split(",") if name.strip()]
        variable_names = list(dict.fromkeys(variable_names))

        invalid_variables = [name for name in variable_names if name not in datatable.variables]
        if invalid_variables:
            invalid = ", ".join(invalid_variables)
            return PipelinePacket.inactive(reason=f"Invalid variable(s): {invalid}")

        variables = {variable: datatable.variables[variable] for variable in variable_names}

        group_by_str = str(self.get_property("group_by"))
        split_mode, factor_name = get_group_by_params(group_by_str)
        if split_mode == SplitMode.FACTOR:
            if not factor_name:
                return PipelinePacket.inactive(reason="No factor selected")
            if factor_name not in datatable.dataset.factors:
                return PipelinePacket.inactive(reason="Invalid factor selected")

        error_bar = str(self.get_property("error_bar"))
        error_bar_type = ERROR_BAR_TYPE.get(error_bar)
        if error_bar_type is None:
            return PipelinePacket.inactive(reason="Invalid error bar type selected")

        # Generate histogram result
        result = get_data_plot_result(
            datatable,
            variables,
            split_mode,
            factor_name,
            error_bar_type,
            figsize=None,
        )

        return PipelinePacket(datatable, report=result.report)
