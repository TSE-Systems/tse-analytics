from dataclasses import dataclass


@dataclass
class Variable:
    name: str
    original_name: str
    unit: str
    original_unit: str
