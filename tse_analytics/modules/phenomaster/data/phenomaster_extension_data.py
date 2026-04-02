from typing import TYPE_CHECKING

from tse_analytics.core.data.datatable import Datatable

if TYPE_CHECKING:
    from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


class PhenoMasterExtensionData:  # noqa: B903
    """
    Base class for PhenoMaster extension data.

    This class provides a common interface for handling data from different PhenoMaster extensions.
    It stores raw data and device information and provides methods for data processing and export.
    """

    def __init__(
        self,
        dataset: PhenoMasterDataset,
        name: str,
        raw_datatable: Datatable,
    ):
        self.dataset = dataset
        self.name = name
        self.raw_datatable = raw_datatable
