from datetime import time

from tse_analytics.core.data.shared import AnimalDiet


class MealDetailsSettings:
    def __init__(
        self,
        sequential_analysis_type: bool,
        intermeal_interval: time,
        drinking_minimum_amount: float,
        feeding_minimum_amount: float,
        fixed_interval: time,
        diets: list[AnimalDiet],
    ):
        self.sequential_analysis_type = sequential_analysis_type
        self.intermeal_interval = intermeal_interval
        self.drinking_minimum_amount = drinking_minimum_amount
        self.feeding_minimum_amount = feeding_minimum_amount
        self.fixed_interval = fixed_interval
        self.diets = diets

    @staticmethod
    def get_default():
        settings = MealDetailsSettings(True, time(minute=5), 0.05, 0.05, time(hour=1), [])
        return settings
