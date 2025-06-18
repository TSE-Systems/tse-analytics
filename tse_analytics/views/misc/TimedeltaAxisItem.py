import pandas as pd
from pyqtgraph import AxisItem


class TimedeltaAxisItem(AxisItem):
    """
    A custom axis item for displaying time deltas on a plot.

    This class extends pyqtgraph's AxisItem to display time values as
    timedeltas (e.g., '00:05:30' for 5 minutes and 30 seconds) instead of
    raw numerical values.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the TimedeltaAxisItem.

        Args:
            *args: Variable length argument list to pass to AxisItem.
            **kwargs: Arbitrary keyword arguments to pass to AxisItem.
        """
        super().__init__(orientation="bottom", **kwargs)
        self.autoSIPrefix = False
        self.fixedHeight = 18

    def tickStrings(self, values, scale, spacing):
        """
        Convert axis values to human-readable timedelta strings.

        This method is called by pyqtgraph to get the string representation
        of tick values for display on the axis.

        Args:
            values: List of numerical values to convert.
            scale: Scale factor for the values.
            spacing: Spacing between tick values.

        Returns:
            List of strings representing the values as timedeltas.
        """
        return [str(pd.to_timedelta(value, unit="s")) for value in values]
