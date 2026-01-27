from NodeGraphQt import BaseNode

from tse_analytics.core.pipeline.pipeline_packet import PipelinePacket


class PipelineNode(BaseNode):
    NODE_NAME = "PipelineNode"

    def __init__(self):
        super().__init__()

        # self.set_color(255, 255, 255)
        # self.model.border_color = (0, 0, 0)
        # self.model.text_color = (127, 0, 0)

    def process(self, packet: PipelinePacket) -> PipelinePacket | dict[str, PipelinePacket]:
        return PipelinePacket.inactive(reason="Not implemented")
