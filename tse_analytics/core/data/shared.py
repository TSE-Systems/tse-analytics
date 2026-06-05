"""
Module containing shared data structures for the data analysis system.

This module defines common data structures used throughout the system,
including enumerations for aggregation and split modes, and dataclasses
for animals, factors, variables, time phases, and animal diets.
"""

from datetime import time, timedelta
from enum import StrEnum, unique
from typing import Annotated, Any, Literal

from pydantic import Field
from pydantic.dataclasses import dataclass


@unique
class Aggregation(StrEnum):
    """
    Enumeration of available aggregation methods for variables.

    Attributes
    ----------
    MEAN : str
        Calculate the mean value.
    MEDIAN : str
        Calculate the median value.
    SUM : str
        Calculate the sum of values.
    MIN : str
        Find the minimum value.
    MAX : str
        Find the maximum value.
    """

    MEAN = "mean"
    MEDIAN = "median"
    SUM = "sum"
    MIN = "min"
    MAX = "max"


@dataclass
class Animal:
    """
    Dataclass representing an animal in the experiment.

    Attributes
    ----------
    id : str
        The unique identifier for the animal.
    properties : dict[str, Any]
        Dictionary of animal properties.
    """

    id: str
    properties: dict[str, Any]


@dataclass
class FactorLevel:
    """
    Dataclass representing a level of a factor.

    Attributes
    ----------
    name : str
        The name of the factor level.
    color : str
        The color used to represent the factor level in visualizations.
    animal_ids : list[str]
        List of animal IDs that belong to this factor level.
    """

    name: str
    color: str
    animal_ids: list[str] = Field(default_factory=list)


@unique
class FactorRole(StrEnum):
    """
    Statistical role of a factor.

    Attributes
    ----------
    BETWEEN_SUBJECT : str
        Factor is constant per subject across all rows (e.g. genotype, group).
    WITHIN_SUBJECT : str
        Factor varies within a subject across rows (e.g. light/dark cycle,
        time phase, trial number).
    """

    BETWEEN_SUBJECT = "between_subject"
    WITHIN_SUBJECT = "within_subject"


@unique
class FactorSource(StrEnum):
    """
    How factor levels are computed for each row of a datatable.

    Attributes
    ----------
    BY_ANIMAL : str
        Levels assigned via explicit per-animal mapping in
        ``FactorLevel.animal_ids``.
    BY_ANIMAL_PROPERTY : str
        Levels derived from a key in ``Animal.properties``.
    BY_TIME_OF_DAY : str
        Levels derived from a row's ``DateTime`` time-of-day (e.g. light/dark
        cycles).
    BY_ELAPSED_TIME : str
        Levels derived from a row's ``Timedelta`` from experiment start
        (named phases).
    BY_COLUMN : str
        Levels read from an existing categorical column on the dataframe.
    BY_TIME_INTERVAL : str
        Sequential integer bins computed from each row's ``Timedelta`` since
        experiment start at a user-defined interval.
    """

    BY_ANIMAL = "by_animal"
    BY_ANIMAL_PROPERTY = "by_animal_property"
    BY_TIME_OF_DAY = "by_time_of_day"
    BY_ELAPSED_TIME = "by_elapsed_time"
    BY_COLUMN = "by_column"
    BY_TIME_INTERVAL = "by_time_interval"


@dataclass
class TimePhase:
    """
    A single named phase used by a ``ByElapsedTimeConfig`` factor.

    Attributes
    ----------
    name : str
        The name of the phase (also the level name).
    start_timestamp : timedelta
        The start of the phase as a timedelta from the experiment start.
    """

    name: str
    start_timestamp: timedelta


@dataclass
class ByAnimalConfig:
    """
    Factor source: levels assigned by explicit ``animal_id -> level`` mapping
    encoded in ``FactorLevel.animal_ids``.
    """

    source: Literal[FactorSource.BY_ANIMAL] = FactorSource.BY_ANIMAL


@dataclass
class ByAnimalPropertyConfig:
    """
    Factor source: levels derived from a key in ``Animal.properties``.

    Attributes
    ----------
    property_key : str
        The key in ``Animal.properties`` whose value provides the level name
        for each animal.
    """

    property_key: str
    source: Literal[FactorSource.BY_ANIMAL_PROPERTY] = FactorSource.BY_ANIMAL_PROPERTY


@dataclass
class ByTimeOfDayConfig:
    """
    Factor source: levels derived from each row's ``DateTime`` time-of-day
    (e.g. ``Light`` / ``Dark`` cycles).

    Attributes
    ----------
    light_cycle_start : time
        The time of day when the light cycle starts.
    dark_cycle_start : time
        The time of day when the dark cycle starts.
    """

    light_cycle_start: time
    dark_cycle_start: time
    source: Literal[FactorSource.BY_TIME_OF_DAY] = FactorSource.BY_TIME_OF_DAY


@dataclass
class ByElapsedTimeConfig:
    """
    Factor source: levels derived from each row's ``Timedelta`` since
    experiment start (named phases).

    Attributes
    ----------
    phases : list[TimePhase]
        Ordered list of phases that define the factor's levels.
    """

    phases: list[TimePhase] = Field(default_factory=list)
    source: Literal[FactorSource.BY_ELAPSED_TIME] = FactorSource.BY_ELAPSED_TIME


@dataclass
class ByColumnConfig:
    """
    Factor source: levels read from an existing categorical column on the
    datatable's dataframe.

    Attributes
    ----------
    column : str
        The name of the column to read level values from.
    """

    column: str
    source: Literal[FactorSource.BY_COLUMN] = FactorSource.BY_COLUMN


@dataclass
class ByTimeIntervalConfig:
    """
    Factor source: sequential integer bins computed from each row's
    ``Timedelta`` at a user-defined interval. Materialized as a ``UInt64``
    column whose values equal ``round(Timedelta / interval)``.

    Attributes
    ----------
    interval : timedelta
        The width of each bin. Must be positive.
    """

    interval: timedelta
    source: Literal[FactorSource.BY_TIME_INTERVAL] = FactorSource.BY_TIME_INTERVAL


FactorConfig = Annotated[
    ByAnimalConfig
    | ByAnimalPropertyConfig
    | ByTimeOfDayConfig
    | ByElapsedTimeConfig
    | ByColumnConfig
    | ByTimeIntervalConfig,
    Field(discriminator="source"),
]


@dataclass
class Factor:
    """
    Dataclass representing a factor in the experiment.

    A factor has two orthogonal first-class attributes:

    - ``role`` (``FactorRole``): the statistical role — between-subject (constant
      per subject) or within-subject (varies within a subject).
    - ``config`` (``FactorConfig``): a discriminated union describing how the
      factor's level values are computed for each row of the datatable.

    Attributes
    ----------
    name : str
        The name of the factor.
    config : FactorConfig
        Discriminated config describing how the factor is computed. Required.
    role : FactorRole
        Statistical role.
    levels : dict[str, FactorLevel]
        List of levels for this factor.
    """

    name: str
    config: FactorConfig
    role: FactorRole
    levels: dict[str, FactorLevel] = Field(default_factory=dict)


@dataclass
class Variable:
    """
    Dataclass representing a variable in the experiment.

    Attributes
    ----------
    name : str
        The name of the variable.
    unit : str
        The unit of measurement for the variable.
    description : str
        A description of the variable.
    type : str
        The data type of the variable.
    aggregation : Aggregation
        The method used to aggregate this variable.
    remove_outliers : bool
        Whether to remove outliers for this variable.
    """

    name: str
    unit: str
    description: str
    type: str
    aggregation: Aggregation
    remove_outliers: bool


@dataclass
class AnimalDiet:
    """
    Dataclass representing an animal diet.

    Attributes
    ----------
    name : str
        The name of the diet.
    caloric_value : float
        The caloric value of the diet.
    """

    name: str
    caloric_value: float
