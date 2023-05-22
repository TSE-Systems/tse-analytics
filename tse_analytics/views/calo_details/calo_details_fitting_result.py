import pandas as pd

from tse_analytics.views.calo_details.fitting_params import FittingParams


class CaloDetailsFittingResult:
    def __init__(
        self,
        name: str,
        description: str,
        params: FittingParams,
        measured: pd.DataFrame,
        rer: list[float]
    ):
        self.name = name
        self.description = description
        self.params = params
        self.measured = measured
        self.rer = rer
