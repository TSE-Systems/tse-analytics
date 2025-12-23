import numpy as np

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.pipeline import PipelineNode


class DescriptiveStatsNode(PipelineNode):
    __identifier__ = "stats"
    NODE_NAME = "Descriptive Statistics"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("result")

    def process(self, datatable: Datatable):
        if datatable is None or not isinstance(datatable, Datatable):
            return None

        descriptive = (
            np
            .round(datatable.active_df.describe(), 3)
            .T[
                [
                    "count",
                    "mean",
                    "std",
                    "min",
                    "max",
                ]
            ]
            .to_html()
        )

        return descriptive
