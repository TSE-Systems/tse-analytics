from enum import Enum, unique


@unique
class BinningOperation(Enum):
    MEAN = 'mean'
    MEDIAN = 'median'
    SUM = 'sum'
