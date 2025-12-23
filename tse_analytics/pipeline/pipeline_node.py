from NodeGraphQt import BaseNode


class PipelineNode(BaseNode):
    NODE_NAME = "PipelineNode"

    def __init__(self):
        super().__init__()

        # self.set_color(255, 255, 255)
        # self.model.border_color = (0, 0, 0)
        # self.model.text_color = (127, 0, 0)
