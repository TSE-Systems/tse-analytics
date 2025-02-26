import pandas as pd

from tse_analytics.modules.phenomaster.submodules.calo.calo_data_settings import CaloDataSettings
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_box import CaloBox


class FittingParams:
    def __init__(
        self,
        calo_details_box: CaloBox,
        general_df: pd.DataFrame,
        details_df: pd.DataFrame,
        ref_details_df: pd.DataFrame,
        calo_details_settings: CaloDataSettings,
    ):
        self.calo_details_box = calo_details_box
        self.general_df = general_df
        self.details_df = details_df
        self.ref_details_df = ref_details_df
        self.calo_details_settings = calo_details_settings
