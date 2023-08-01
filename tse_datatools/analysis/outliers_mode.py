from enum import Enum, unique


@unique
class OutliersMode(Enum):
    OFF = "Detection Off"
    HIGHLIGHT = "Highlight outliers"
    REMOVE = "Remove outliers"
