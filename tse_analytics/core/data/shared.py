"""
Module containing shared data structures for the data analysis system.

This module defines common data structures used throughout the system,
including enumerations for aggregation and split modes, and dataclasses
for animals, factors, variables, time phases, and animal diets.
"""

from dataclasses import dataclass, field
from enum import StrEnum, unique
from typing import Any

import pandas as pd


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


@unique
class SplitMode(StrEnum):
    """
    Enumeration of available modes for splitting data.

    Attributes
    ----------
    ANIMAL : str
        Split data by animal.
    FACTOR : str
        Split data by factor.
    RUN : str
        Split data by run.
    TOTAL : str
        No splitting, use total data.
    """

    ANIMAL = "Animal"
    FACTOR = "Factor"
    RUN = "Run"
    TOTAL = "Total"


@dataclass
class Animal:
    """
    Dataclass representing an animal in the experiment.

    Attributes
    ----------
    enabled : bool
        Whether the animal is enabled in the analysis.
    id : str
        The unique identifier for the animal.
    color : str
        The color used to represent the animal in visualizations.
    properties : dict[str, Any]
        Dictionary of animal properties.
    """

    enabled: bool
    id: str
    color: str
    properties: dict[str, Any]

    def get_dict(self):
        """
        Get a dictionary representation of the animal.

        Returns
        -------
        dict
            Dictionary containing the animal's attributes.
        """
        return self.__dict__


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
    animal_ids: list[str] = field(default_factory=list)


@dataclass
class Factor:
    """
    Dataclass representing a factor in the experiment.

    Attributes
    ----------
    name : str
        The name of the factor.
    levels : list[FactorLevel]
        List of levels for this factor.
    """

    name: str
    levels: list[FactorLevel] = field(default_factory=list)


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

    def get_dict(self):
        """
        Get a dictionary representation of the variable.

        Returns
        -------
        dict
            Dictionary containing the variable's attributes.
        """
        return self.__dict__


@dataclass
class TimePhase:
    """
    Dataclass representing a time phase in the experiment.

    Attributes
    ----------
    name : str
        The name of the time phase.
    start_timestamp : pd.Timedelta
        The start time of the phase as a timedelta from the experiment start.
    """

    name: str
    start_timestamp: pd.Timedelta


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
