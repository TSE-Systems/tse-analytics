import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.shared import Variable, Aggregation
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.io import tse_import_settings
from tse_analytics.modules.phenomaster.submodules.grouphousing.data.grouphousing_data import GroupHousingData


def read_grouphousing(path: Path, dataset: PhenoMasterDataset) -> GroupHousingData:
    metadata = dataset.metadata["tables"][tse_import_settings.GROUP_HOUSING_TABLE]
    hardware_metadata = dataset.metadata["hardware"][tse_import_settings.GROUP_HOUSING_TABLE]

    # Read variables list
    dtypes = {}
    for item in metadata["columns"].values():
        variable = Variable(
            item["id"],
            item["unit"],
            item["description"],
            item["type"],
            Aggregation.MEAN,
            False,
        )
        dtypes[variable.name] = item["type"]
    # Ignore the time for "DateTime" columns
    # dtypes.pop("StartDateTime")
    # dtypes.pop("EndDateTime")

    dtypes["EndDateTime"] = "Int64"
    dtypes["Animal"] = str

    # Read measurements data
    df = pd.DataFrame()
    with sqlite3.connect(path, check_same_thread=False) as connection:
        for chunk in pd.read_sql_query(
            f"SELECT * FROM {tse_import_settings.GROUP_HOUSING_TABLE}",
            connection,
            dtype=dtypes,
            chunksize=tse_import_settings.CHUNK_SIZE,
        ):
            df = pd.concat([df, chunk], ignore_index=True)

    # Convert DateTime from POSIX format
    df["StartDateTime"] = pd.to_datetime(df["StartDateTime"], origin="unix", unit="ns")
    df["EndDateTime"] = pd.to_datetime(df["EndDateTime"], origin="unix", unit="ns")
    # Insert Duration column
    df.insert(
        df.columns.get_loc("EndDateTime") + 1,
        "Duration",
        df["EndDateTime"] - df["StartDateTime"],
    )

    # Convert dict keys type from str to int
    channel_to_channel_type_mapping = {int(k): v for k, v in hardware_metadata["channels"].items()}
    df.insert(
        df.columns.get_loc("Channel") + 1,
        "ChannelType",
        df["Channel"].replace(channel_to_channel_type_mapping),
    )

    df = df.astype({
        "Animal": "category",
        "ChannelType": "category",
    })

    df.sort_values(by=["StartDateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    data = GroupHousingData(
        dataset,
        tse_import_settings.GROUP_HOUSING_TABLE,
        str(path),
        df,
    )

    return data


def import_grouphousing_csv_data(
    filename: str, dataset: PhenoMasterDataset, csv_import_settings: CsvImportSettings
) -> GroupHousingData | None:
    path = Path(filename)
    if path.is_file() and path.suffix.lower() == ".csv":
        return _load_from_csv(path, dataset, csv_import_settings)
    return None


def _load_from_csv(path: Path, dataset: PhenoMasterDataset, csv_import_settings: CsvImportSettings) -> GroupHousingData:
    dtype = {
        "Number": np.int64,
        "Date": str,
        "Time": str,
        "BoxNo": np.int64,
        "ChannelNo": np.int64,
        "Channel type": str,
        "Animal": str,
    }

    df = pd.read_csv(
        path,
        delimiter=csv_import_settings.delimiter,
        decimal=csv_import_settings.decimal_separator,
        skiprows=1,  # Skip header part
        low_memory=False,
        dtype=dtype,
    )

    # Rename table columns
    df.rename(
        columns={
            "BoxNo": "Box",
            "ChannelNo": "Channel",
            "Channel type": "ChannelType",
        },
        inplace=True,
    )

    # Convert DateTime column
    df.insert(
        0,
        "StartDateTime",
        pd.to_datetime(
            df["Date"] + " " + df["Time"],
            dayfirst=csv_import_settings.day_first,
            format=csv_import_settings.datetime_format if csv_import_settings.use_datetime_format else None,
        ),
    )
    df.insert(
        df.columns.get_loc("StartDateTime") + 1,
        "EndDateTime",
        df["StartDateTime"],
    )

    df.drop(columns=["Date", "Time", "Number"], inplace=True)

    df = df.astype({
        "Animal": "category",
        "ChannelType": "category",
    })

    # TODO: fix the bug with channels offset +1 in CSV export?
    df["Channel"] = df["Channel"] - 1

    df.sort_values(by=["StartDateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    data = GroupHousingData(
        dataset,
        tse_import_settings.GROUP_HOUSING_TABLE,
        str(path),
        df,
    )
    return data
