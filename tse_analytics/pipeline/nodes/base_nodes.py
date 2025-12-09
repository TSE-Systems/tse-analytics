"""Base nodes for pipeline editor."""

from NodeGraphQt import BaseNode


class IfElseNode(BaseNode):
    """Conditional branch node that routes data based on a boolean condition."""

    __identifier__ = "pipeline.control"
    NODE_NAME = "If/Else"

    def __init__(self):
        super().__init__()
        self.add_input("data")
        self.add_input("condition")
        self.add_output("true")
        self.add_output("false")
        self.set_color(50, 150, 200)

    def process(self, data, condition):
        """
        Route data to either 'true' or 'false' output based on condition.
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


class ConditionNode(BaseNode):
    """Evaluates a condition and outputs a boolean result."""

    __identifier__ = "pipeline.control"
    NODE_NAME = "Condition"

    def __init__(self):
        super().__init__()
        self.add_input("value")
        self.add_output("result")
        self.set_color(50, 150, 200)

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


class DatasetOutputNode(BaseNode):
    """Node for outputting processed dataset."""

    __identifier__ = "pipeline.output"
    NODE_NAME = "Dataset Output"

    def __init__(self):
        super().__init__()
        self.add_input("dataset", color=(180, 80, 80))
        self.create_property("output_name", "processed_data")

    def set_dataset(self, dataset):
        """Set the output dataset."""
        self._output_dataset = dataset

    def get_dataset(self):
        """Get the output dataset."""
        return getattr(self, "_output_dataset", None)


class ViewerNode(BaseNode):
    """Node for visualizing data at any pipeline stage."""

    __identifier__ = "pipeline.viewer"
    NODE_NAME = "Data Viewer"

    def __init__(self):
        super().__init__()
        self.add_input("dataset", color=(180, 80, 80))
        self.add_output("dataset", color=(180, 80, 80))
        self.create_property("auto_view", True)

    def view_data(self, dataset):
        """Display the data (to be connected to a viewer widget)."""
        # This will be implemented when we add the viewer functionality
        if dataset is not None:
            print(f"Viewing dataset: {dataset}")
