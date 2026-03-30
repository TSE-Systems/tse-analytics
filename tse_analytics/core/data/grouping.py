from dataclasses import dataclass
from enum import StrEnum, unique


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
    TOTAL : str
        No splitting, use total data.
    """

    ANIMAL = "Animal"
    FACTOR = "Factor"
    RUN = "Run"
    TOTAL = "Total"


@dataclass
class GroupingSettings:
    mode: GroupingMode = GroupingMode.ANIMAL
    factor_name: str | None = None
