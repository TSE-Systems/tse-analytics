from typing import Literal

import pandas as pd


class BinningParams:
    def __init__(self, timedelta: pd.Timedelta, operation: Literal["sum", "mean", "median"]):
        self.timedelta = timedelta
        self.operation = operation
