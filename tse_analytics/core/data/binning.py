"""
Module for time binning functionality in data analysis.

This module provides classes for configuring different types of time binning,
including fixed time intervals, light/dark cycles, and custom time phases.
"""

from datetime import time, timedelta

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class TimeIntervalsBinningSettings:
    """
    Settings for binning data into fixed time intervals.

    Attributes
    ----------
    unit : str
        The time unit for intervals (e.g., "hour", "minute").
    delta : int
        The number of units per interval.
    """

    unit: str
    delta: int


@dataclass
class TimeCyclesBinningSettings:
    """
    Settings for binning data into light and dark cycles.

    Attributes
    ----------
    light_cycle_start : time
        The time when the light cycle starts.
    dark_cycle_start : time
        The time when the dark cycle starts.
    """

    light_cycle_start: time
    dark_cycle_start: time


@dataclass
class TimePhasesBinningSettings:
    """
    Settings for binning data into custom time phases.

    Attributes
    ----------
    time_phases : list[TimePhase]
        List of time phases to bin data into.
    """

    time_phases: list[TimePhase] = Field(default_factory=list)


@dataclass
class TimePhase:
    """
    Dataclass representing a time phase in the experiment.

    Attributes
    ----------
    name : str
        The name of the time phase.
    start_timestamp : timedelta
        The start time of the phase as a timedelta from the experiment start.
    """

    name: str
    start_timestamp: timedelta
