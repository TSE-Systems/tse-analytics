from dataclasses import dataclass


@dataclass
class CaloBox:
    box: int
    ref_box: int | None
