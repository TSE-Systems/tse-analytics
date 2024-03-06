class MealDetailsSettings:
    def __init__(
        self,
        iterations: int,
        prediction_offset: int,
        flow: float,
    ):
        self.iterations = iterations
        self.prediction_offset = prediction_offset
        self.flow = flow


def get_default_settings():
    settings = MealDetailsSettings(
        10000,
        50,
        0.5,
    )
    return settings
