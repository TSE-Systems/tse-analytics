from dataclasses import dataclass


@dataclass
class GroupHousingAnimalItem:
    box: int
    animal: str
    factors: dict[str, str | None]
