from dataclasses import dataclass


@dataclass
class Box:
    id: int
    animal_id: int

    def get_dict(self):
        return self.__dict__
