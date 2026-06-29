from NodeGraphQt.widgets.node_widgets import NodeComboBox

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode
from tse_analytics.pipeline.pipeline_packet import PipelinePacket
from tse_analytics.toolbox.umap.processor import get_umap_result

METRICS = [
    "euclidean",
    "manhattan",
    "chebyshev",
    "minkowski",
    "canberra",
    "braycurtis",
    "haversine",
    "mahalanobis",
    "wminkowski",
    "seuclidean",
    "cosine",
    "correlation",
]


class UmapNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "UMAP"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

        self.add_text_input(
            "variables",
            "",
            "",
            "Variables",
            "Comma-separated variable names",
        )

        self.add_combo_menu(
            "group_by",
            "Group by",
            items=[],
            tooltip="Grouping mode",
        )

        self.add_text_input(
            "n_neighbors",
            "n_neighbors",
            "15",
            "n_neighbors",
            "Number of neighbors (1-100)",
        )

        self.add_text_input(
            "n_components",
            "n_components",
            "2",
            "n_components",
            "Number of components (1-3)",
        )

        self.add_combo_menu(
            "metric",
            "Metric",
            items=METRICS,
            tooltip="Distance metric",
        )

        self.add_text_input(
            "min_dist",
            "min_dist",
            "0.1",
            "min_dist",
            "Minimum distance (0.001-0.5)",
        )

    def initialize(self, dataset: Dataset, datatable: Datatable):
        if datatable is None:
            group_by_options = ["Animal"]
        else:
            group_by_options = datatable.get_group_by_columns()

        group_by_widget: NodeComboBox = self.get_widget("group_by")
        group_by_widget.clear()
        group_by_widget.add_items(group_by_options)

    def process(self, packet: PipelinePacket) -> PipelinePacket:
        datatable = packet.value
        if datatable is None or not isinstance(datatable, Datatable):
            return PipelinePacket.inactive(reason="Invalid input datatable")

        # Parse variables
        variables_raw = str(self.get_property("variables")).strip()
        if not variables_raw:
            return PipelinePacket.inactive(reason="No variables selected")

        variable_names = [name.strip() for name in variables_raw.replace(";", ",").split(",") if name.strip()]
        variable_names = list(dict.fromkeys(variable_names))
        if len(variable_names) < 3:
            return PipelinePacket.inactive(reason="Select at least three variables")

        invalid_variables = [name for name in variable_names if name not in datatable.variables]
        if invalid_variables:
            invalid = ", ".join(invalid_variables)
            return PipelinePacket.inactive(reason=f"Invalid variable(s): {invalid}")

        # Parse group_by
        factor_name = str(self.get_property("group_by"))

        # Parse n_neighbors
        try:
            n_neighbors = int(self.get_property("n_neighbors"))
            if n_neighbors < 1 or n_neighbors > 100:
                return PipelinePacket.inactive(reason="n_neighbors must be between 1 and 100")
        except ValueError, TypeError:
            return PipelinePacket.inactive(reason="Invalid n_neighbors value")

        # Parse n_components
        try:
            n_components = int(self.get_property("n_components"))
            if n_components < 1 or n_components > 3:
                return PipelinePacket.inactive(reason="n_components must be between 1 and 3")
        except ValueError, TypeError:
            return PipelinePacket.inactive(reason="Invalid n_components value")

        # Parse min_dist
        try:
            min_dist = float(self.get_property("min_dist"))
            if min_dist < 0.001 or min_dist > 0.5:
                return PipelinePacket.inactive(reason="min_dist must be between 0.001 and 0.5")
        except ValueError, TypeError:
            return PipelinePacket.inactive(reason="Invalid min_dist value")

        metric = str(self.get_property("metric"))

        # Perform UMAP analysis
        result = get_umap_result(
            datatable,
            variable_names,
            factor_name,
            n_neighbors,
            n_components,
            metric,
            min_dist,
        )

        return PipelinePacket(datatable, report=result.report)
