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

    @staticmethod
    def get_default():
        settings = MealDetailsSettings(
            time(minute=10),
            0.001,
            0.01,
        )
        return settings
