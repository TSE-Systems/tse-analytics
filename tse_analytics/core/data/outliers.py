from enum import Enum, unique


@unique
class OutliersMode(Enum):
    OFF = "Detection Off"
    HIGHLIGHT = "Highlight outliers"
    REMOVE = "Remove outliers"


class OutliersParams:
    def __init__(self, mode: OutliersMode, coefficient: float):
        self.mode = mode
        self.coefficient = coefficient
