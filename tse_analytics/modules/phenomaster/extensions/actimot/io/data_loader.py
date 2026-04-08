from pathlib import Path

import connectorx as cx
import numpy as np
import pandas as pd

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.phenomaster.io.tse_import_settings import ACTIMOT_RAW_TABLE


def read_actimot_raw(path: Path, dataset: Dataset) -> Datatable:
    metadata = dataset.metadata["tables"][ACTIMOT_RAW_TABLE]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    df = cx.read_sql(
        f"sqlite:///{path}",
        f"SELECT DateTime, Box, X1, X2, Y1 AS Y FROM {ACTIMOT_RAW_TABLE}",
        return_type="pandas",
    )

    # Convert types
    df = df.astype({"Box": "UInt16"}, errors="ignore")

    df["X"] = np.left_shift(df["X2"].to_numpy(dtype=np.uint64), 32) + df["X1"].to_numpy(dtype=np.uint64)
    df = df.drop(columns=["X1", "X2"])

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns").dt.as_unit(TIME_RESOLUTION_UNIT)

    box_to_animal_map = {animal.properties["Box"]: animal.id for animal in dataset.animals.values()}
    df.insert(
        df.columns.get_loc("Box"),
        "Animal",
        df["Box"].map(box_to_animal_map),
    )

    # Add Timedelta columns
    df.insert(
        loc=1,
        column="Timedelta",
        value=(df["DateTime"] - dataset.experiment_started),
    )

    # Convert categorical types
    df = df.astype({
        "Animal": "category",
        "Box": "category",
    })

    raw_datatable = Datatable(
        dataset,
        ACTIMOT_RAW_TABLE,
        f"Raw {ACTIMOT_RAW_TABLE} datatable",
        {},
        df,
        {
            "origin_path": str(path),
            "sample_interval": sample_interval,
        },
    )

    return raw_datatable


def import_actimot_csv_data(
    filename: str,
    dataset: Dataset,
    csv_import_settings: CsvImportSettings,
) -> Datatable | None:
    path = Path(filename)
    if not path.is_file() or path.suffix.lower() != ".csv":
        return None

    with open(path) as f:
        lines = f.readlines()

        header_template = "Rel. [s];BoxNr;"
        # looping through each line in the file
        for idx, line in enumerate(lines):
            if header_template in line:
                header_line_number = idx
                columns_line = line
                break

    datetime_column_header = columns_line.split(csv_import_settings.delimiter)[0]

    usecols = [datetime_column_header, "Rel. [s]", "BoxNr", "X (cm)", "Y (cm)", "X", "Y"]

    dtype = {
        datetime_column_header: "string",
        "Rel. [s]": "Float64",
        "BoxNr": "UInt16",
        "X (cm)": "Float64",
        "Y (cm)": "Float64",
        "X": "string",
        "Y": "string",
    }

    # for i in range(1, 65):
    #     usecols.append(f"X{i}")
    #     dtype[f"X{i}"] = "UInt8"
    #
    # for i in range(1, 33):
    #     usecols.append(f"Y{i}")
    #     dtype[f"Y{i}"] = "UInt8"

    df = pd.read_csv(
        path,
        delimiter=csv_import_settings.delimiter,
        decimal=csv_import_settings.decimal_separator,
        skiprows=header_line_number,  # Skip header part
        low_memory=True,
        usecols=usecols,
        dtype=dtype,
        dtype_backend="numpy_nullable",
        na_values=["-"],
    )

    # Rename table columns
    df.rename(columns={datetime_column_header: "DateTime", "BoxNr": "Box"}, inplace=True)

    # Convert DateTime column
    df["DateTime"] = pd.to_datetime(
        df["DateTime"],
        format=csv_import_settings.datetime_format if csv_import_settings.use_datetime_format else "mixed",
        dayfirst=csv_import_settings.day_first,
    ).dt.as_unit(TIME_RESOLUTION_UNIT)

    box_to_animal_map = {}
    for animal in dataset.animals.values():
        box_to_animal_map[animal.properties["Box"]] = animal.id

    df.insert(
        df.columns.get_loc("Box") + 1,
        "Animal",
        None,
    )

    df["Animal"] = df["Box"].astype("Int16")
    df.replace({"Animal": box_to_animal_map}, inplace=True)

    df = df.sort_values(["Box", "DateTime"])
    df.reset_index(drop=True, inplace=True)

    # Add Timedelta columns
    df.insert(
        loc=1,
        column="Timedelta",
        value=(df["DateTime"] - dataset.experiment_started),
    )

    # convert categorical types
    df = df.astype({
        "Animal": "category",
    })

    # Sampling interval
    sample_interval = df.iloc[1].at["DateTime"] - df.iloc[0].at["DateTime"]

    raw_datatable = Datatable(
        dataset,
        ACTIMOT_RAW_TABLE,
        f"Raw {ACTIMOT_RAW_TABLE} datatable",
        {},
        df,
        {
            "origin_path": str(path),
            "sample_interval": sample_interval,
        },
    )

    return raw_datatable
