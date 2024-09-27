from datetime import datetime, time
from enum import Enum, unique, StrEnum

from tse_analytics.core.data.shared import TimePhase


@unique
class BinningMode(StrEnum):
    INTERVALS = "Time Intervals"
    CYCLES = "Light/Dark Cycles"
    PHASES = "Time Phases"


@unique
class BinningOperation(Enum):
    MEAN = "mean"
    MEDIAN = "median"
    SUM = "sum"


class BinningParams:
    def __init__(self, apply: bool, mode: BinningMode, operation: BinningOperation):
        self.apply = apply
        self.mode = mode
        self.operation = operation


class TimeIntervalsBinningSettings:
    def __init__(self, unit: str, delta: int):
        self.unit = unit
        self.delta = delta


class TimeCyclesBinningSettings:
    def __init__(self, light_cycle_start: datetime.time, dark_cycle_start: datetime.time):
        self.light_cycle_start = light_cycle_start
        self.dark_cycle_start = dark_cycle_start


class TimePhasesBinningSettings:
    def __init__(self, time_phases: list[TimePhase]):
        self.time_phases = time_phases


class BinningSettings:
    def __init__(self):
        self.time_intervals_settings = TimeIntervalsBinningSettings("hour", 1)
        self.time_cycles_settings = TimeCyclesBinningSettings(time(7, 0), time(19, 0))
        self.time_phases_settings = TimePhasesBinningSettings([])
