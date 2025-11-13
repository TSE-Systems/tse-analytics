from dataclasses import dataclass


@dataclass
class DrinkFeedAnimalItem:
    box: int
    animal: str
    diet: float | None
    factors: dict[str, str | None]
