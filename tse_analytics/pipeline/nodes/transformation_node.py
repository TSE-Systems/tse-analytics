import numpy as np
from scipy.stats import boxcox, yeojohnson

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket


class TransformationNode(PipelineNode):
    __identifier__ = "transformation"
    NODE_NAME = "Transformation"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("datatable")

        self.add_text_input(
            "variable",
            "",
            "",
            "Variable to transform",
            "Variable to transform",
        )

        self.add_text_input(
            "transformed_variable",
            "",
            "",
            "Transformed variable",
            "Transformed variable",
        )

        self.add_combo_menu(
            "method",
            "Method",
            items=[
                "Box-Cox",
                "Yeo-Johnson",
                "Log",
                "Log10",
            ],
            tooltip="Transformation method",
        )

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")

        variable = str(self.get_property("variable"))
        transformed_variable = str(self.get_property("transformed_variable"))
        method = str(self.get_property("method"))

        result_datatable = datatable.clone()
        data = result_datatable.active_df[variable].to_numpy()

        match method:
            case "Box-Cox":
                transformed_data, lambda_opt = boxcox(data)
            case "Yeo-Johnson":
                transformed_data, lambda_opt = yeojohnson(data)
            case "Log":
                transformed_data = np.log(data)
                lambda_opt = None
            case "Log10":
                transformed_data = np.log10(data)
                lambda_opt = None

        result_datatable.active_df[transformed_variable] = transformed_data

        tooltip = f"<h3>Transformation</h3>Method: {method}<br>Lambda: {lambda_opt:.5f}"
        self.view.setToolTip(tooltip)

        return PipelinePacket(result_datatable, report=tooltip, meta={"lambda": lambda_opt})
