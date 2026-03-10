from dataclasses import dataclass

import pandas as pd

from tse_analytics.modules.phenomaster.extensions.calo.calo_settings import CaloSettings
from tse_analytics.modules.phenomaster.extensions.calo.data.calo_box import CaloBox


@dataclass
class FittingParams:
    calo_box: CaloBox
    main_df: pd.DataFrame
    box_df: pd.DataFrame
    ref_df: pd.DataFrame
    calo_settings: CaloSettings
