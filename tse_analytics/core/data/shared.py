"""
Module containing shared data structures for the data analysis system.

This module defines common data structures used throughout the system,
including enumerations for aggregation and split modes, and dataclasses
for animals, factors, variables, time phases, and animal diets.
"""

from enum import StrEnum, unique
from typing import Any

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
    color : str
        The color used to represent the animal in visualizations.
    properties : dict[str, Any]
        Dictionary of animal properties.
    """

    id: str
    color: str
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
    levels: list[FactorLevel] = Field(default_factory=list)


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
