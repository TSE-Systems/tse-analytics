from NodeGraphQt import BaseNode

from tse_analytics.pipeline.pipeline_packet import PipelinePacket


class PipelineNode(BaseNode):
    NODE_NAME = "PipelineNode"

    def __init__(self):
        super().__init__()

        # self.set_color(255, 255, 255)
        # self.model.border_color = (160, 180, 178)
        # self.model.text_color = (45, 60, 58)

    def process(self, packet: PipelinePacket) -> PipelinePacket | dict[str, PipelinePacket]:
        return PipelinePacket.inactive(reason="Not implemented")
