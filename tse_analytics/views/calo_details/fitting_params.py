import pandas as pd

from tse_analytics.views.calo_details.calo_details_settings import CaloDetailsSettings


class FittingParams:
    def __init__(
        self,
        box_number: int,
        ref_box_number: int,
        general_df: pd.DataFrame,
        details_df: pd.DataFrame,
        ref_details_df: pd.DataFrame,
        calo_details_settings: CaloDetailsSettings,
    ):
        self.box_number = box_number
        self.ref_box_number = ref_box_number
        self.general_df = general_df
        self.details_df = details_df
        self.ref_details_df = ref_details_df
        self.calo_details_settings = calo_details_settings
