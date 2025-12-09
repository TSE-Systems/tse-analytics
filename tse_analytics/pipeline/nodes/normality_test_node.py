from NodeGraphQt import BaseNode
from NodeGraphQt.widgets.node_widgets import NodeComboBox
from scipy.stats import kstest, normaltest, shapiro

from tse_analytics.core import manager
from tse_analytics.core.data.datatable import Datatable


class NormalityTestNode(BaseNode):
    __identifier__ = "pipeline.test"
    NODE_NAME = "Normality"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("yes")
        self.add_output("no")

        self.add_combo_menu(
            "method",
            "Method",
            items=["Shapiro-Wilk", "Kolmogorov-Smirnov", "D’Agostino",],
            tooltip="Test method",
        )

        self.add_combo_menu(
            "variable",
            "Variable",
            items=[],
            tooltip="Please select a variable to test",
        )
        self.initialize()

    def initialize(self):
        datatable = manager.get_selected_datatable()
        if datatable is None:
            variable_names = ["No variables"]
        else:
            variable_names = datatable.variables.keys()
        widget: NodeComboBox = self.get_widget("variable")
        widget.clear()
        widget.add_items(variable_names)

    def process(self, datatable: Datatable):
        """
        Test for normality and route data through appropriate output.
        Returns tuple of (yes_output, no_output) based on test result.
        """
        if datatable is None or not isinstance(datatable, Datatable):
            return None, None

        method = str(self.get_property("method"))
        variable = str(self.get_property("variable"))

        data = datatable.active_df[variable]

        if method == "Shapiro-Wilk":
            stat, pvalue = shapiro(data)
        elif method == "Kolmogorov-Smirnov":
            stat, pvalue = kstest(data, "norm")
        elif method == "D'Agostino":
            stat, pvalue = normaltest(data)

        # pyrefly: ignore [unbound-name]
        is_normal = pvalue > 0.05

        # pyrefly: ignore [unbound-name]
        tooltip = f"<b>Result</b><br/>Statistic: {stat:.5f}<br/>P-value: {pvalue:.5f}<br/>Normal: {is_normal}"
        self.view.setToolTip(tooltip)

        # Return data through appropriate port
        return (datatable, None) if is_normal else (None, datatable)
