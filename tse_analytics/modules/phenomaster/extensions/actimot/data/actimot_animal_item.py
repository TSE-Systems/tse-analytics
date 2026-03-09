from dataclasses import dataclass


@dataclass
class ActimotAnimalItem:
    box: int
    animal: str
    factors: dict[str, str | None]
