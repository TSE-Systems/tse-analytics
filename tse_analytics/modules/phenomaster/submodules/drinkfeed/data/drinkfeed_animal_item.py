class DrinkFeedAnimalItem:
    def __init__(self, box: int, animal: str, diet: float | None, factors: dict[str, str | None]):
        self.box = box
        self.animal = animal
        self.diet = diet
        self.factors = factors
