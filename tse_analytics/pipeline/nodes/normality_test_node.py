from NodeGraphQt.widgets.node_widgets import NodeComboBox
from scipy.stats import anderson, kstest, shapiro

from tse_analytics.core import manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket


class NormalityTestNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Normality"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("yes")
        self.add_output("no")

        self.add_text_input(
            "variable",
            "",
            "",
            "Variable to test",
            "Variable to test",
        )

        self.add_combo_menu(
            "method",
            "Method",
            items=[
                "Shapiro-Wilk",
                "Kolmogorov-Smirnov",
                "Anderson-Darling",
            ],
            tooltip="Test method",
        )

    def initialize(self, dataset: Dataset):
        datatable = manager.get_selected_datatable()
        if datatable is None:
            variable_names = ["No variables"]
        else:
            variable_names = datatable.variables.keys()
        widget: NodeComboBox = self.get_widget("variable")
        widget.clear()
        widget.add_items(variable_names)

    def process(self, packet: PipelinePacket) -> dict[str, PipelinePacket]:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return {
                "yes": PipelinePacket.inactive(reason="Invalid input datatable"),
                "no": PipelinePacket.inactive(reason="Invalid input datatable"),
            }

        variable = str(self.get_property("variable"))
        method = str(self.get_property("method"))

        data = datatable.active_df[variable]

        match method:
            case "Shapiro-Wilk":
                statistic, pvalue = shapiro(data)
            case "Kolmogorov-Smirnov":
                statistic, pvalue = kstest(data, "norm")
            case "Anderson-Darling":
                statistic, pvalue = anderson(data, dist="norm", method="interpolate")

        is_normal = pvalue > 0.05

        tooltip = f"<b>Result</b><br/>Statistic: {statistic:.5f}<br/>P-value: {pvalue:.5f}<br/>Normal: {is_normal}"
        self.view.setToolTip(tooltip)

        if is_normal:
            return {
                "yes": PipelinePacket(
                    datatable,
                    meta={
                        "normal": True,
                        "selected_variable": variable,
                    },
                ),
                "no": PipelinePacket.inactive(normal=False, selected_variable=variable),
            }
        else:
            return {
                "yes": PipelinePacket.inactive(normal=True, selected_variable=variable),
                "no": PipelinePacket(
                    datatable,
                    meta={
                        "normal": False,
                        "selected_variable": variable,
                    },
                ),
            }
