from typing import TYPE_CHECKING

import pandas as pd

from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.data.phenomaster_extension_data import PhenoMasterExtensionData

if TYPE_CHECKING:
    from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


class DrinkFeedRawData(PhenoMasterExtensionData):
    def __init__(
        self,
        dataset: PhenoMasterDataset,
        name: str,
        path: str,
        variables: dict[str, Variable],
        raw_df: pd.DataFrame,
    ):
        super().__init__(
            dataset,
            name,
            raw_df,
            variables,
            meta={
                "origin_path": path,
            },
        )
