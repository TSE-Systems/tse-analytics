from dataclasses import dataclass


@dataclass
class Animal:
    id: int
    box_id: int
    weight: float
    text1: str
    text2: str
    text3: str

    def get_dict(self):
        return self.__dict__
