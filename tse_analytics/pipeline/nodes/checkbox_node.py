from tse_analytics.pipeline.pipeline_node import PipelineNode


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

    def process(self, input):
        state = self.get_property("state")
        return (input, None) if state else (None, input)
