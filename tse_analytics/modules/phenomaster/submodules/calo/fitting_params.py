import pandas as pd

from tse_analytics.modules.phenomaster.submodules.calo.calo_settings import CaloSettings
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_box import CaloBox


class FittingParams:
    def __init__(
        self,
        calo_box: CaloBox,
        main_df: pd.DataFrame,
        box_df: pd.DataFrame,
        ref_box_df: pd.DataFrame,
        calo_settings: CaloSettings,
    ):
        self.calo_box = calo_box
        self.main_df = main_df
        self.box_df = box_df
        self.ref_df = ref_box_df
        self.calo_settings = calo_settings
