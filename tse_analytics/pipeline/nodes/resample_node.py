import pandas as pd
from NodeGraphQt import BaseNode, constants

from tse_analytics.core.data.datatable import Datatable


class ResampleNode(BaseNode):
    __identifier__ = "pipeline.table"
    NODE_NAME = "Resample"

    def __init__(self):
        super().__init__()
        self.add_input("datatable")
        self.add_output("resampled")

        self.create_property(
            "unit",
            "hour",
            items=["day", "hour", "minute"],
            widget_type=constants.NodePropWidgetEnum.QCOMBO_BOX.value,
            widget_tooltip="Timedelta unit",
        )
        self.create_property(
            "delta",
            1,
            widget_type=constants.NodePropWidgetEnum.QLINE_EDIT.value,
            widget_tooltip="Timedelta value",
        )

    def process(self, datatable: Datatable):
        if datatable is None or not isinstance(datatable, Datatable):
            return None

        unit = str(self.get_property("unit"))
        delta = int(self.get_property("delta"))

        resampling_interval = pd.to_timedelta(delta, unit=unit)

        result = datatable.clone()
        result.resample(resampling_interval)

        return result
