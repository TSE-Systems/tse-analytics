from typing import TYPE_CHECKING

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.modules.phenomaster.data.phenomaster_extension_data import PhenoMasterExtensionData

if TYPE_CHECKING:
    from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


class DrinkFeedRawData(PhenoMasterExtensionData):
    def __init__(
        self,
        dataset: PhenoMasterDataset,
        name: str,
        raw_datatable: Datatable,
    ):
        super().__init__(
            dataset,
            name,
            raw_datatable,
        )
