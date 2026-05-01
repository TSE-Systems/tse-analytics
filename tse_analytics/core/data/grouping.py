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
    RUN : str
        Split data by run.
    """

    ANIMAL = "Animal"
    FACTOR = "Factor"
    RUN = "Run"


@dataclass
class GroupingSettings:
    mode: GroupingMode = GroupingMode.ANIMAL
    factor_name: str = ""
