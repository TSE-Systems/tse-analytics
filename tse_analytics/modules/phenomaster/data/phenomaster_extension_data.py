from typing import TYPE_CHECKING, Any

import pandas as pd

from tse_analytics.core.data.shared import Variable

if TYPE_CHECKING:
    from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


class PhenoMasterExtensionData:
    """
    Base class for PhenoMaster extension data.

    This class provides a common interface for handling data from different PhenoMaster extensions.
    It stores raw data and device information and provides methods for data processing and export.
    """

    def __init__(
        self,
        dataset: PhenoMasterDataset,
        name: str,
        raw_df: pd.DataFrame,
        variables: dict[str, Variable],
        meta: dict[str, Any],
    ):
        """
        Initialize an ExtensionData object.

        Args:
            dataset (PhenoMasterDataset): The parent dataset.
            name (str): The name of the extension.
            raw_df (pd.DataFrame): Dictionary mapping data types to DataFrames.
            variables (dict[str, Variable]): Available variables.
            meta (dict[str, Any]): Additional metadata.
        """
        self.dataset = dataset
        self.name = name
        self.raw_df = raw_df
        self.variables = variables
        self.meta = meta

    @property
    def start_timestamp(self) -> pd.Timestamp:
        return self.raw_df.at[0, "DateTime"]

    @property
    def origin_path(self) -> str | None:
        return self.meta.get("origin_path", None)

    @property
    def sampling_interval(self) -> pd.Timedelta | None:
        return self.meta.get("sampling_interval", None)
