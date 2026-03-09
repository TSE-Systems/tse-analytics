from dataclasses import dataclass

import pandas as pd

from tse_analytics.modules.phenomaster.extensions.calo.fitting_params import FittingParams


@dataclass
class FittingResult:
    box_number: int
    params: FittingParams
    df: pd.DataFrame
