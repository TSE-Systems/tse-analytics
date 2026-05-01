from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.matrix_plot.processor import MATRIXPLOT_KIND, get_matrix_plot_result


class MatrixPlotNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Matrix Plot"

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
            "plot_type",
            "Plot Type",
            items=list(MATRIXPLOT_KIND.keys()),
            tooltip="Plot type",
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

        variables_raw = str(self.get_property("variables")).strip()
        if not variables_raw:
            return PipelinePacket.inactive(reason="No variables selected")

        variable_names = [name.strip() for name in variables_raw.replace(";", ",").split(",") if name.strip()]
        variable_names = list(dict.fromkeys(variable_names))
        if len(variable_names) < 2:
            return PipelinePacket.inactive(reason="Select at least two variables")

        invalid_variables = [name for name in variable_names if name not in datatable.variables]
        if invalid_variables:
            invalid = ", ".join(invalid_variables)
            return PipelinePacket.inactive(reason=f"Invalid variable(s): {invalid}")

        factor_name = str(self.get_property("group_by"))

        plot_type = str(self.get_property("plot_type"))
        plot_kind = MATRIXPLOT_KIND.get(plot_type)
        if plot_kind is None:
            return PipelinePacket.inactive(reason="Invalid plot type selected")

        result = get_matrix_plot_result(
            datatable,
            variable_names,
            factor_name,
            plot_kind,
            figsize=None,
        )

        return PipelinePacket(datatable, report=result.report)
