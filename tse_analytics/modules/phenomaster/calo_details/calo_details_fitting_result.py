import pandas as pd

from tse_analytics.modules.phenomaster.calo_details.fitting_params import FittingParams


class CaloDetailsFittingResult:
    def __init__(
        self,
        box_number: str,
        params: FittingParams,
        df: pd.DataFrame,
    ):
        self.box_number = box_number
        self.params = params
        self.df = df
