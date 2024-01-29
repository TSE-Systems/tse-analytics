from enum import Enum, unique


@unique
class BinningMode(Enum):
    INTERVALS = "Time Intervals"
    CYCLES = "Light/Dark Cycles"
    PHASES = "Time Phases"
