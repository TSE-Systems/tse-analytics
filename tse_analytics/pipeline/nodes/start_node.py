from NodeGraphQt import BaseNode


class StartNode(BaseNode):
    __identifier__ = "pipeline"

    NODE_NAME = "Start"

    def __init__(self):
        super().__init__()

        self.add_output("output")

    def initialize(self):
        print(f"{self.NODE_NAME} initialized")

    def process(self):
        print(f"{self.NODE_NAME} processed")
