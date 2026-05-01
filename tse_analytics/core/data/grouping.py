from enum import StrEnum, unique

from pydantic.dataclasses import dataclass


@unique
class GroupingMode(StrEnum):
    """
    Enumeration of available modes for splitting data.

    Attributes
    ----------
    ANIMAL : str
        Split data by animal.
    FACTOR : str
        Split data by factor.
    """

    ANIMAL = "Animal"
    FACTOR = "Factor"


@dataclass
class GroupingSettings:
    mode: GroupingMode = GroupingMode.ANIMAL
    factor_name: str = ""
