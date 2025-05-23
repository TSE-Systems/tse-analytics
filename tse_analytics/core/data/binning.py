from datetime import time
from enum import StrEnum, unique

from tse_analytics.core.data.shared import TimePhase


@unique
class BinningMode(StrEnum):
    INTERVALS = "Time Intervals"
    CYCLES = "Light/Dark Cycles"
    PHASES = "Time Phases"


class BinningSettings:
    def __init__(self):
        self.apply = False
        self.mode = BinningMode.INTERVALS
        self.time_intervals_settings = TimeIntervalsBinningSettings("hour", 1)
        self.time_cycles_settings = TimeCyclesBinningSettings(time(7, 0), time(19, 0))
        self.time_phases_settings = TimePhasesBinningSettings([])


class TimeIntervalsBinningSettings:
    def __init__(self, unit: str, delta: int):
        self.unit = unit
        self.delta = delta


class TimeCyclesBinningSettings:
    def __init__(self, light_cycle_start: time, dark_cycle_start: time):
        self.light_cycle_start = light_cycle_start
        self.dark_cycle_start = dark_cycle_start


class TimePhasesBinningSettings:
    def __init__(self, time_phases: list[TimePhase]):
        self.time_phases = time_phases
