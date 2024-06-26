from pandas._libs.missing import NAType


class MealDetailsAnimalItem:
    def __init__(self, box: str, animal: str, diet: float | NAType, factors: dict[str, str | None]):
        self.box = box
        self.animal = animal
        self.diet = diet
        self.factors = factors
