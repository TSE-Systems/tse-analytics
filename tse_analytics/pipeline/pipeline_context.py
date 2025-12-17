from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable


class PipelineContext:
    def __init__(self) -> None:
        self.selected_dataset: Dataset | None = None
        self.selected_datatable: Datatable | None = None
        self.selected_variable: Variable | None = None
