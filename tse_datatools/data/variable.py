from dataclasses import dataclass


@dataclass
class Variable:
    name: str
    unit: str

    def get_dict(self):
        return self.__dict__
