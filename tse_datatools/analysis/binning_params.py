import pandas as pd

from tse_datatools.analysis.binning_operation import BinningOperation


class BinningParams:
    def __init__(self, timedelta: pd.Timedelta, operation: BinningOperation):
        self.timedelta = timedelta
        self.operation = operation
