from pyqtgraph import AxisItem


class TimedeltaAxisItem(AxisItem):
    sampling_interval = None

    def __init__(self, *args, **kwargs):
        super().__init__(orientation="bottom", **kwargs)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        formatStrings = []
        if self.sampling_interval is not None:
            for value in values:
                dt = self.sampling_interval * value
                formatStrings.append(str(dt))
        return formatStrings
