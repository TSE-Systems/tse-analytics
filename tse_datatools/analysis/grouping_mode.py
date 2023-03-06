from enum import Enum, unique


@unique
class GroupingMode(Enum):
    ANIMALS = 'Animals'
    FACTORS = 'Factors'
    RUNS = 'Runs'
