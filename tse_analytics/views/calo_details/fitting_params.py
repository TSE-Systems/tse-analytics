import pandas as pd

from tse_analytics.views.calo_details.calo_details_settings import CaloDetailsSettings
from tse_datatools.data.calo_details_box import CaloDetailsBox


class FittingParams:
    def __init__(
        self,
        calo_details_box: CaloDetailsBox,
        general_df: pd.DataFrame,
        details_df: pd.DataFrame,
        ref_details_df: pd.DataFrame,
        calo_details_settings: CaloDetailsSettings,
    ):
        self.calo_details_box = calo_details_box
        self.general_df = general_df
        self.details_df = details_df
        self.ref_details_df = ref_details_df
        self.calo_details_settings = calo_details_settings
