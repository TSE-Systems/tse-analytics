from tse_analytics.pipeline.pipeline_node import PipelineNode


class IfElseNode(PipelineNode):
    """Conditional branch node that routes data based on a boolean condition."""

    __identifier__ = "control"
    NODE_NAME = "If/Else"

    def __init__(self):
        super().__init__()
        self.add_input("data")
        self.add_input("condition")
        self.add_output("true")
        self.add_output("false")

    def process(self, data, condition):
        """
        Route data to either 'true' or 'false' output based on the condition.
        Returns tuple of (true_output, false_output).
        """
        if condition is None:
            return None, None

        if isinstance(condition, bool):
            result = condition
        else:
            # Try to convert to bool
            result = bool(condition)

        return (data, None) if result else (None, data)
