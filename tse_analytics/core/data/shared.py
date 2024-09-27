from dataclasses import dataclass, field
from enum import Enum, unique, StrEnum

import pandas as pd


@unique
class Aggregation(StrEnum):
    MEAN = "mean"
    MEDIAN = "median"
    SUM = "sum"
    MIN = "min"
    MAX = "max"


@unique
class SplitMode(Enum):
    ANIMAL = "Animal"
    FACTOR = "Factor"
    RUN = "Run"
    TOTAL = "Total"


@dataclass
class Animal:
    enabled: bool
    id: str
    box: int
    weight: float
    text1: str
    text2: str
    text3: str

    def get_dict(self):
        return self.__dict__


@dataclass
class Group:
    name: str
    animal_ids: list[str] = field(default_factory=list)


@dataclass
class Factor:
    name: str
    groups: list[Group] = field(default_factory=list)


@dataclass
class Variable:
    name: str
    unit: str
    description: str
    type: str
    aggregation: Aggregation
    outliers: bool

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
