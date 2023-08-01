from tse_datatools.analysis.outliers_mode import OutliersMode


class OutliersParams:
    def __init__(self, mode: OutliersMode, coefficient: float):
        self.mode = mode
        self.coefficient = coefficient
