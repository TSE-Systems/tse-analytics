from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class MealEpisode:
    sensor: str
    animal: int
    box: int
    id: int
    start: datetime
    duration: timedelta
    offset: timedelta
    gap: timedelta
    quantity: float
    rate: float
