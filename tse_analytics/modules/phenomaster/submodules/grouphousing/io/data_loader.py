from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.submodules.grouphousing.data.grouphousing_data import GroupHousingData


def import_grouphousing_csv_data(
    filename: str, dataset: PhenoMasterDataset, csv_import_settings: CsvImportSettings
) -> GroupHousingData | None:
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
        "Animal": str,
    }

    raw_df = pd.read_csv(
        path,
        delimiter=csv_import_settings.delimiter,
        decimal=csv_import_settings.decimal_separator,
        skiprows=1,  # Skip header part
        low_memory=False,
        dtype=dtype,
    )

    # Rename table columns
    raw_df.rename(
        columns={
            "BoxNo": "Box",
            "ChannelNo": "Channel",
            "Channel type": "ChannelType",
        },
        inplace=True,
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
    raw_df.drop(columns=["Date", "Time", "Number"], inplace=True)

    raw_df.sort_values(by=["DateTime"], inplace=True)
    raw_df.reset_index(drop=True, inplace=True)

    data = GroupHousingData(
        dataset,
        "GroupHousing",
        str(path),
        raw_df,
    )
    return data
