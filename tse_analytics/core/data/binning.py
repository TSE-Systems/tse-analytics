"""
Module for time binning functionality in data analysis.

This module provides classes for configuring different types of time binning,
including fixed time intervals, light/dark cycles, and custom time phases.
"""

from datetime import time
from enum import StrEnum, unique

from tse_analytics.core.data.shared import TimePhase


@unique
class BinningMode(StrEnum):
    """
    Enumeration of available binning modes.

    Attributes
    ----------
    INTERVALS : str
        Bin data into fixed time intervals.
    CYCLES : str
        Bin data into light and dark cycles.
    PHASES : str
        Bin data into custom time phases.
    """
    INTERVALS = "Time Intervals"
    CYCLES = "Light/Dark Cycles"
    PHASES = "Time Phases"


class BinningSettings:
    """
    Settings for time binning configuration.

    This class holds the configuration for time binning, including the mode
    and specific settings for each binning mode.
    """
    def __init__(self):
        """
        Initialize default binning settings.
        """
        self.apply = False
        self.mode = BinningMode.INTERVALS
        self.time_intervals_settings = TimeIntervalsBinningSettings("hour", 1)
        self.time_cycles_settings = TimeCyclesBinningSettings(time(7, 0), time(19, 0))
        self.time_phases_settings = TimePhasesBinningSettings([])


class TimeIntervalsBinningSettings:
    """
    Settings for binning data into fixed time intervals.
    """
    def __init__(self, unit: str, delta: int):
        """
        Initialize time intervals binning settings.

        Parameters
        ----------
        unit : str
            The time unit for intervals (e.g., "hour", "minute").
        delta : int
            The number of units per interval.
        """
        self.unit = unit
        self.delta = delta


class TimeCyclesBinningSettings:
    """
    Settings for binning data into light and dark cycles.
    """
    def __init__(self, light_cycle_start: time, dark_cycle_start: time):
        """
        Initialize light/dark cycles binning settings.

        Parameters
        ----------
        light_cycle_start : time
            The time when the light cycle starts.
        dark_cycle_start : time
            The time when the dark cycle starts.
        """
        self.light_cycle_start = light_cycle_start
        self.dark_cycle_start = dark_cycle_start


class TimePhasesBinningSettings:
    """
    Settings for binning data into custom time phases.
    """
    def __init__(self, time_phases: list[TimePhase]):
        """
        Initialize time phases binning settings.

        Parameters
        ----------
        time_phases : list[TimePhase]
            List of time phases to bin data into.
        """
        self.time_phases = time_phases
