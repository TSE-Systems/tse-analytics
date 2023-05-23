import pandas as pd

from tse_analytics.views.calo_details.fitting_params import FittingParams


class CaloDetailsFittingResult:
    def __init__(
        self,
        name: str,
        params: FittingParams,
        measured: pd.DataFrame,
        rer: list[float]
    ):
        self.name = name
        self.params = params
        self.measured = measured
        self.rer = rer
