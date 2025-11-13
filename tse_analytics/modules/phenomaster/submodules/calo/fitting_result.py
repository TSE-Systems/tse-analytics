import pandas as pd

from tse_analytics.modules.phenomaster.submodules.calo.fitting_params import FittingParams


class FittingResult:
    def __init__(
        self,
        box_number: int,
        params: FittingParams,
        df: pd.DataFrame,
    ):
        self.box_number = box_number
        self.params = params
        self.df = df
