from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.correlation_matrix.processor import get_correlation_matrix_result


class CorrelationMatrixNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Correlation Matrix"

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

        df = datatable.get_df(
            variable_names,
            SplitMode.ANIMAL,
            "",
        )

        result = get_correlation_matrix_result(
            datatable.dataset,
            df,
            variable_names,
            figsize=None,
        )

        return PipelinePacket(datatable, report=result.report)
