from pandas._libs.missing import NAType


class MealDetailsBox:
    def __init__(self, box: int, animal: int, diet: float | NAType):
        self.box = box
        self.animal = animal
        self.diet = diet
