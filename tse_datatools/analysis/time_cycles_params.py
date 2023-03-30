from datetime import datetime


class TimeCyclesParams:
    def __init__(self, apply: bool, light_cycle_start: datetime.time, dark_cycle_start: datetime.time):
        self.apply = apply
        self.light_cycle_start = light_cycle_start
        self.dark_cycle_start = dark_cycle_start
