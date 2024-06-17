from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, unique


@unique
class GroupingMode(Enum):
    ANIMALS = "Animals"
    FACTORS = "Factors"
    RUNS = "Runs"


@dataclass
class Animal:
    enabled: bool
    id: int
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
    animal_ids: list[int] = field(default_factory=list)


@dataclass
class Factor:
    name: str
    groups: list[Group] = field(default_factory=list)


@dataclass
class Variable:
    name: str
    unit: str
    description: str

    def get_dict(self):
        return self.__dict__


@dataclass
class TimePhase:
    name: str
    start_timestamp: datetime


@dataclass
class AnimalDiet:
    name: str
    caloric_value: float
