from enum import Enum, unique


@unique
class GroupingMode(Enum):
    ANIMALS = 'Animals'
    GROUPS = 'Groups'
    RUNS = 'Runs'
