from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.submodules.trafficage.data.trafficage_data import TraffiCageData


def import_trafficage_csv_data(
    filename: str, dataset: PhenoMasterDataset, csv_import_settings: CsvImportSettings
) -> TraffiCageData | None:
    path = Path(filename)
    if path.is_file() and path.suffix.lower() == ".csv":
        return _load_from_csv(path, dataset, csv_import_settings)
    return None


def _load_from_csv(path: Path, dataset: PhenoMasterDataset, csv_import_settings: CsvImportSettings):
    dtype = {
        "Number": np.int64,
        "Date": str,
        "Time": str,
        "BoxNo": np.int64,
        "ChannelNo": np.int64,
        "Channel type": str,
        "Tag": str,
    }

    raw_df = pd.read_csv(
        path,
        delimiter=csv_import_settings.delimiter,
        decimal=csv_import_settings.decimal_separator,
        skiprows=1,  # Skip header part
        low_memory=False,
        dtype=dtype,
    )

    # Convert DateTime column
    raw_df.insert(
        0,
        "DateTime",
        pd.to_datetime(
            raw_df["Date"] + " " + raw_df["Time"],
            dayfirst=csv_import_settings.day_first,
            format=csv_import_settings.datetime_format if csv_import_settings.use_datetime_format else None,
        ),
    )
    raw_df.drop(columns=["Date", "Time"], inplace=True)

    # Calo sampling interval
    sampling_interval = raw_df.iloc[1].at["DateTime"] - raw_df.iloc[0].at["DateTime"]

    variables: dict[str, Variable] = {}

    data = TraffiCageData(
        dataset,
        "TraffiCage",
        str(path),
        variables,
        raw_df,
        sampling_interval,
    )
    return data
