from dataclasses import dataclass, field

from tse_datatools.data.group import Group


@dataclass
class Factor:
    name: str
    groups: list[Group] = field(default_factory=list)
