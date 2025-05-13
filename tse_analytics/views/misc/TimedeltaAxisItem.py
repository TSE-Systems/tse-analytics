import pandas as pd
from pyqtgraph import AxisItem


class TimedeltaAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(orientation="bottom", **kwargs)
        self.autoSIPrefix = False
        self.fixedHeight = 18

    def tickStrings(self, values, scale, spacing):
        return [str(pd.to_timedelta(value, unit="s")) for value in values]
