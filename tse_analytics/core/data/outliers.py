from enum import unique, StrEnum


@unique
class OutliersMode(StrEnum):
    OFF = "Outliers detection off"
    HIGHLIGHT = "Highlight outliers"
    REMOVE = "Remove outliers"


class OutliersSettings:
    def __init__(self, mode: OutliersMode, coefficient: float):
        self.mode = mode
        self.coefficient = coefficient
