from pathlib import Path

import connectorx as cx
import pandas as pd

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.core.utils.data import sanitize_dtypes
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.phenomaster.io.tse_import_settings import GROUP_HOUSING_TABLE


def read_grouphousing(path: Path, dataset: Dataset) -> Datatable:
    metadata = dataset.metadata["tables"][GROUP_HOUSING_TABLE]
    hardware_metadata = dataset.metadata["hardware"][GROUP_HOUSING_TABLE]

    # Read variable list
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

    dtypes["EndDateTime"] = "Int64"
    dtypes["Animal"] = "string"

    dtypes = sanitize_dtypes(dtypes)

    # Read measurement data
    df = cx.read_sql(
        f"sqlite:///{path}",
        f"SELECT * FROM {GROUP_HOUSING_TABLE}",
        return_type="pandas",
    )

    # Convert types according to metadata
    df = df.astype(dtypes, errors="ignore")

    # Convert DateTime from POSIX format
    df["StartDateTime"] = pd.to_datetime(df["StartDateTime"], origin="unix", unit="ns").dt.as_unit(TIME_RESOLUTION_UNIT)
    df["EndDateTime"] = pd.to_datetime(df["EndDateTime"], origin="unix", unit="ns").dt.as_unit(TIME_RESOLUTION_UNIT)
    # Insert Duration column
    df.insert(
        df.columns.get_loc("EndDateTime") + 1,
        "Duration",
        df["EndDateTime"] - df["StartDateTime"],
    )

    # Convert dict keys type from str to int
    channel_to_channel_type_mapping = {str(k): v for k, v in hardware_metadata["channels"].items()}
    df.insert(
        df.columns.get_loc("Channel") + 1,
        "ChannelType",
        df["Channel"].astype("string").replace(channel_to_channel_type_mapping),
    )

    df = df.astype({
        "Animal": "category",
        "ChannelType": "category",
    })

    df.sort_values(by=["StartDateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Add Timedelta columns
    df.insert(
        loc=1,
        column="Timedelta",
        value=(df["StartDateTime"] - dataset.experiment_started).dt.as_unit(TIME_RESOLUTION_UNIT),
    )

    animal_ids = df["Animal"].unique().tolist()
    animal_ids.sort()

    raw_datatable = Datatable(
        dataset,
        GROUP_HOUSING_TABLE,
        f"Raw {GROUP_HOUSING_TABLE} datatable",
        {},
        df,
        {
            "origin_path": str(path),
            "animal_ids": animal_ids,
        },
    )
    return raw_datatable


def import_grouphousing_csv_data(
    filename: str,
    dataset: Dataset,
    csv_import_settings: CsvImportSettings,
) -> Datatable | None:
    path = Path(filename)
    if not path.is_file() or path.suffix.lower() != ".csv":
        return None

    dtype = {
        "Number": "UInt64",
        "Date": "string",
        "Time": "string",
        "BoxNo": "UInt16",
        "ChannelNo": "UInt8",
        "Channel type": "string",
        "Animal": "string",
    }

    df = pd.read_csv(
        path,
        delimiter=csv_import_settings.delimiter,
        decimal=csv_import_settings.decimal_separator,
        skiprows=1,  # Skip header part
        low_memory=False,
        dtype=dtype,
        dtype_backend="numpy_nullable",
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
        ).dt.as_unit(TIME_RESOLUTION_UNIT),
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

    # Add Timedelta columns
    df.insert(
        loc=1,
        column="Timedelta",
        value=(df["StartDateTime"] - dataset.experiment_started).dt.as_unit(TIME_RESOLUTION_UNIT),
    )

    animal_ids = df["Animal"].unique().tolist()
    animal_ids.sort()

    raw_datatable = Datatable(
        dataset,
        GROUP_HOUSING_TABLE,
        f"Raw {GROUP_HOUSING_TABLE} datatable",
        {},
        df,
        {
            "origin_path": str(path),
            "animal_ids": animal_ids,
        },
    )
    return raw_datatable
