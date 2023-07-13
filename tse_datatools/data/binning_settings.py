from datetime import time

from tse_datatools.data.time_cycles_binning_settings import TimeCyclesBinningSettings
from tse_datatools.data.time_intervals_binning_settings import TimeIntervalsBinningSettings
from tse_datatools.data.time_phases_binning_settings import TimePhasesBinningSettings


class BinningSettings:
    def __init__(self):
        self.time_intervals_settings = TimeIntervalsBinningSettings("hour", 1)
        self.time_cycles_settings = TimeCyclesBinningSettings(time(7, 0), time(19, 0))
        self.time_phases_settings = TimePhasesBinningSettings([])
