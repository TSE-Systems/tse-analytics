from datetime import time


class MealDetailsSettings:
    def __init__(
        self,
        intermeal_interval: time,
        drinking_minimum_amount: float,
        feeding_minimum_amount: float,
    ):
        self.intermeal_interval = intermeal_interval
        self.drinking_minimum_amount = drinking_minimum_amount
        self.feeding_minimum_amount = feeding_minimum_amount


def get_default_settings():
    settings = MealDetailsSettings(
        time(minute=10),
        0.1,
        0.1,
    )
    return settings
