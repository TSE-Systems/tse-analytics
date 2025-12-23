from tse_analytics.pipeline import PipelineNode


class StartNode(PipelineNode):
    __identifier__ = "input"

    NODE_NAME = "Start"

    def __init__(self):
        super().__init__()

        self.add_output("output")

    def initialize(self):
        print(f"{self.NODE_NAME} initialized")

    def process(self):
        print(f"{self.NODE_NAME} processed")
