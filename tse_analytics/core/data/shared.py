from dataclasses import dataclass, field
from enum import StrEnum, unique
from typing import Any

import pandas as pd


@unique
class Aggregation(StrEnum):
    MEAN = "mean"
    MEDIAN = "median"
    SUM = "sum"
    MIN = "min"
    MAX = "max"


@unique
class SplitMode(StrEnum):
    ANIMAL = "Animal"
    FACTOR = "Factor"
    RUN = "Run"
    TOTAL = "Total"


@dataclass
class Animal:
    enabled: bool
    id: str
    properties: dict[str, Any]

    def get_dict(self):
        return self.__dict__


@dataclass
class FactorLevel:
    name: str
    animal_ids: list[str] = field(default_factory=list)


@dataclass
class Factor:
    name: str
    levels: list[FactorLevel] = field(default_factory=list)


@dataclass
class Variable:
    name: str
    unit: str
    description: str
    type: str
    aggregation: Aggregation
    remove_outliers: bool

    def get_dict(self):
        return self.__dict__


@dataclass
class TimePhase:
    name: str
    start_timestamp: pd.Timedelta


@dataclass
class AnimalDiet:
    name: str
    caloric_value: float
