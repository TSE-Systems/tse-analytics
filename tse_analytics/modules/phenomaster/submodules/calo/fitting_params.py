import pandas as pd

from tse_analytics.modules.phenomaster.submodules.calo.calo_settings import CaloSettings
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_box import CaloBox


class FittingParams:
    def __init__(
        self,
        calo_box: CaloBox,
        main_df: pd.DataFrame,
        details_df: pd.DataFrame,
        ref_details_df: pd.DataFrame,
        calo_data_settings: CaloSettings,
    ):
        self.calo_box = calo_box
        self.main_df = main_df
        self.details_df = details_df
        self.ref_details_df = ref_details_df
        self.calo_data_settings = calo_data_settings
