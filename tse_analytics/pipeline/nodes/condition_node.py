from tse_analytics.pipeline.pipeline_node import PipelineNode


class ConditionNode(PipelineNode):
    """Evaluates a condition and outputs a boolean result."""

    __identifier__ = "control"
    NODE_NAME = "Condition"

    def __init__(self):
        super().__init__()
        self.add_input("value")
        self.add_output("result")

        self.add_combo_menu(
            "operator",
            "Operator",
            items=["==", "!=", ">", "<", ">=", "<=", "is None", "is not None"],
            tooltip="Comparison operator",
        )
        self.add_text_input("compare_value", "Compare Value", text="")

    def process(self, value):
        """Evaluate the condition and return boolean result."""
        operator = str(self.get_property("operator"))
        compare_str = str(self.get_property("compare_value"))

        if operator == "is None":
            return value is None
        elif operator == "is not None":
            return value is not None

        if value is None:
            return False

        # Try to convert compare_value to the same type as value
        try:
            if isinstance(value, (int, float)):
                compare_value = float(compare_str)
            else:
                compare_value = compare_str

            if operator == "==":
                return value == compare_value
            elif operator == "!=":
                return value != compare_value
            elif operator == ">":
                return value > compare_value
            elif operator == "<":
                return value < compare_value
            elif operator == ">=":
                return value >= compare_value
            elif operator == "<=":
                return value <= compare_value
        except (ValueError, TypeError):
            return False

        return False
