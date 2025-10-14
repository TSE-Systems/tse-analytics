import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.shared import Variable, Aggregation
from tse_analytics.modules.phenomaster.io import tse_import_settings
from tse_analytics.modules.phenomaster.submodules.actimot.data.actimot_data import ActimotData
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


def read_actimot_raw(path: Path, dataset: PhenoMasterDataset) -> ActimotData:
    metadata = dataset.metadata["tables"][tse_import_settings.ACTIMOT_RAW_TABLE]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    skipped_variables = ["DateTime", "Box", "X1", "X2", "Y1", "Y2", "Z1", "Z2"]
    variables: dict[str, Variable] = {}
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
        if variable.name not in skipped_variables:
            variables[variable.name] = variable
        dtypes[variable.name] = item["type"]
    # Ignore the time for "DateTime" column
    dtypes.pop("DateTime")

    # Read measurements data
    df = pd.DataFrame()
    with sqlite3.connect(path, check_same_thread=False) as connection:
        for chunk in pd.read_sql_query(
            f"SELECT * FROM {tse_import_settings.ACTIMOT_RAW_TABLE}",
            connection,
            dtype=dtypes,
            chunksize=tse_import_settings.CHUNK_SIZE,
        ):
            chunk["X"] = np.left_shift(chunk["X2"].to_numpy(dtype=np.uint64), 32) + chunk["X1"].to_numpy(
                dtype=np.uint64
            )
            chunk.rename(columns={"Y1": "Y"}, inplace=True)
            chunk.drop(columns=["X1", "X2"], inplace=True)
            df = pd.concat([df, chunk], ignore_index=True)

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns")

    actimot_data = ActimotData(
        dataset,
        tse_import_settings.ACTIMOT_RAW_TABLE,
        str(path),
        variables,
        df,
        sample_interval,
    )

    return actimot_data


def import_actimot_csv_data(
    filename: str, dataset: PhenoMasterDataset, csv_import_settings: CsvImportSettings
) -> ActimotData | None:
    path = Path(filename)
    if path.is_file() and path.suffix.lower() == ".csv":
        return _load_from_csv(path, dataset, csv_import_settings)
    return None


def _load_from_csv(path: Path, dataset: PhenoMasterDataset, csv_import_settings: CsvImportSettings) -> ActimotData:
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
        datetime_column_header: str,
        "Rel. [s]": np.float64,
        "BoxNr": np.uint8,
        "X (cm)": np.float64,
        "Y (cm)": np.float64,
        "X": str,
        "Y": str,
    }

    # for i in range(1, 65):
    #     usecols.append(f"X{i}")
    #     dtype[f"X{i}"] = np.uint8
    #
    # for i in range(1, 33):
    #     usecols.append(f"Y{i}")
    #     dtype[f"Y{i}"] = np.uint8

    raw_df = pd.read_csv(
        path,
        delimiter=csv_import_settings.delimiter,
        decimal=csv_import_settings.decimal_separator,
        skiprows=header_line_number,  # Skip header part
        low_memory=True,
        usecols=usecols,
        dtype=dtype,
        na_values=["-"],
    )

    # Rename table columns
    raw_df.rename(columns={datetime_column_header: "DateTime", "BoxNr": "Box"}, inplace=True)

    # Convert DateTime column
    raw_df["DateTime"] = pd.to_datetime(
        raw_df["DateTime"],
        format=csv_import_settings.datetime_format if csv_import_settings.use_datetime_format else "mixed",
        dayfirst=csv_import_settings.day_first,
    )

    box_to_animal_map = {}
    for animal in dataset.animals.values():
        box_to_animal_map[animal.properties["Box"]] = animal.id

    new_df = raw_df.copy()

    new_df.insert(
        new_df.columns.get_loc("Box") + 1,
        "Animal",
        None,
    )

    new_df["Animal"] = new_df["Box"].astype(int)
    new_df.replace({"Animal": box_to_animal_map}, inplace=True)

    new_df = new_df.sort_values(["Box", "DateTime"])
    new_df.reset_index(drop=True, inplace=True)

    # convert categorical types
    new_df = new_df.astype({
        "Animal": "category",
    })

    # Sampling interval
    sampling_interval = new_df.iloc[1].at["DateTime"] - new_df.iloc[0].at["DateTime"]

    variables: dict[str, Variable] = {}

    actimot_data = ActimotData(
        dataset,
        "ActiMot",
        str(path),
        variables,
        new_df,
        sampling_interval,
    )
    return actimot_data
