import pandas as pd

from tse_analytics.views.calo_details.fitting_params import FittingParams


class CaloDetailsFittingResult:
    def __init__(
        self,
        box_number: int,
        params: FittingParams,
        rer_df: pd.DataFrame,
    ):
        self.box_number = box_number
        self.params = params
        self.rer_df = rer_df
