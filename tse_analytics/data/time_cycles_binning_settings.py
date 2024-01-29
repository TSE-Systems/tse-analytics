from datetime import datetime


class TimeCyclesBinningSettings:
    def __init__(self, light_cycle_start: datetime.time, dark_cycle_start: datetime.time):
        self.light_cycle_start = light_cycle_start
        self.dark_cycle_start = dark_cycle_start
