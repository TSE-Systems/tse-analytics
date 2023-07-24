from tse_datatools.analysis.binning_mode import BinningMode
from tse_datatools.analysis.binning_operation import BinningOperation


class BinningParams:
    def __init__(self, apply: bool, mode: BinningMode, operation: BinningOperation):
        self.apply = apply
        self.mode = mode
        self.operation = operation
