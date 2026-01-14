from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket


class CheckboxNode(PipelineNode):
    __identifier__ = "control"
    NODE_NAME = "Checkbox"

    def __init__(self):
        super().__init__()

        # create input and output port.
        self.add_input("in")
        self.add_output("true")
        self.add_output("false")

        # create the checkboxes.
        self.add_checkbox("state", "", "State", False)

    def process(self, packet: PipelinePacket) -> dict[str, PipelinePacket]:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return {
                "true": PipelinePacket.inactive(reason="Invalid input datatable"),
                "false": PipelinePacket.inactive(reason="Invalid input datatable"),
            }

        state = self.get_property("state")

        if state:
            return {
                "true": PipelinePacket(datatable),
                "false": PipelinePacket.inactive(),
            }
        else:
            return {
                "true": PipelinePacket.inactive(),
                "false": PipelinePacket(datatable),
            }
