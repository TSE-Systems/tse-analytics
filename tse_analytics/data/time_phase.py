from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimePhase:
    name: str
    start_timestamp: datetime
