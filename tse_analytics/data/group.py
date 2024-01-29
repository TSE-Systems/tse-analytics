from dataclasses import dataclass, field


@dataclass
class Group:
    name: str
    animal_ids: list[int] = field(default_factory=list)
