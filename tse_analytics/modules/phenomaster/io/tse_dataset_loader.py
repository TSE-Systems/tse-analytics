import json
import sqlite3
import timeit
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

from tse_analytics.core.data.shared import Aggregation, Animal, Factor, Variable
from tse_analytics.core.predefined_variables import assign_predefined_values
from tse_analytics.core.tse_import_settings import TseImportSettings
from tse_analytics.modules.phenomaster.actimot.data.actimot_details import ActimotDetails
from tse_analytics.modules.phenomaster.calo_details.data.calo_details import CaloDetails
from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.modules.phenomaster.meal_details.data.meal_details import MealDetails

CHUNK_SIZE = 1000000

ACTIMOT_RAW_TABLE = "actimot_raw"
DRINKFEED_BIN_TABLE = "drinkfeed_bin"
CALO_BIN_TABLE = "calo_bin"


def load_tse_dataset(path: Path, import_settings: TseImportSettings) -> Dataset | None:
    tic = timeit.default_timer()

    metadata = _read_metadata(path)
    animals = _get_animals(metadata["animals"])
    # factors = TseDatasetLoader._get_factors(metadata["groups"])

    main_table_df, main_table_vars, main_table_sampling_interval = _read_main_table(path, metadata["tables"], animals)

    # Assign predefined variables properties
    main_table_vars = assign_predefined_values(main_table_vars)

    dataset = Dataset(
        name=metadata["experiment"]["experiment_no"],
        path=str(path),
        meta=metadata,
        animals=animals,
        variables=main_table_vars,
        df=main_table_df,
        sampling_interval=main_table_sampling_interval,
    )

    # Import ActoMot raw data if present
    if import_settings.import_actimot_raw:
        if ACTIMOT_RAW_TABLE in metadata["tables"]:
            actimot_details = _read_actimot_raw(path, metadata["tables"], dataset)
            dataset.actimot_details = actimot_details

    # Import drinkfeed bin data if present
    if import_settings.import_drinkfeed_bin:
        if DRINKFEED_BIN_TABLE in metadata["tables"]:
            meal_details = _read_drinkfeed_bin(path, metadata["tables"], dataset)
            dataset.meal_details = meal_details

    # Import calo bin data if present
    if import_settings.import_calo_bin:
        if CALO_BIN_TABLE in metadata["tables"]:
            calo_details = _read_calo_bin(path, metadata["tables"], dataset)
            dataset.calo_details = calo_details

    logger.info(f"Import complete in {(timeit.default_timer() - tic):.3f} sec: {path}")

    return dataset


def _read_metadata(path: Path) -> dict:
    with sqlite3.connect(path, check_same_thread=False) as connection:
        df = pd.read_sql_query(
            "SELECT * FROM metadata",
            connection,
        )
        metadata_str = df.iloc[0]["json"]
    metadata = json.loads(metadata_str)

    # Convert animal IDs to strings
    for item in metadata["animals"].values():
        item["id"] = str(item["id"])

    # Convert time intervals from [ms] to Timedeltas
    metadata["experiment"]["runtime"] = str(pd.to_timedelta(metadata["experiment"]["runtime"], unit="ms"))
    metadata["experiment"]["cycle_interval"] = str(pd.to_timedelta(metadata["experiment"]["cycle_interval"], unit="ms"))

    if "main_table" in metadata["tables"]:
        metadata["tables"]["main_table"]["sample_interval"] = str(
            pd.to_timedelta(metadata["tables"]["main_table"]["sample_interval"], unit="ms")
        )

    if "actimot_raw" in metadata["tables"]:
        metadata["tables"]["actimot_raw"]["sample_interval"] = str(
            pd.to_timedelta(metadata["tables"]["actimot_raw"]["sample_interval"], unit="ms")
        )

    return metadata


def _get_animals(data: dict) -> dict[str, Animal]:
    animals: dict[str, Animal] = {}
    for item in data.values():
        animal = Animal(
            enabled=bool(item["enabled"]),
            id=str(item["id"]),
            box=int(item["box"]),
            weight=float(item["weight"]),
            text1=item["text1"],
            text2=item["text2"],
            text3=item["text3"],
        )
        animals[animal.id] = animal
    return animals


def _get_factors(data: dict) -> dict[str, Factor]:
    factors: dict[str, Factor] = {}
    for item in data.values():
        factor = Factor(name=item["id"])
        factors[factor.name] = factor
    return factors


def _add_cumulative_columns(df: pd.DataFrame, origin_name: str, variables: dict[str, Variable]):
    cols = [col for col in df.columns if origin_name in col]
    for col in cols:
        cumulative_col_name = col + "C"
        df[cumulative_col_name] = df.groupby("Box", observed=False)[col].transform(pd.Series.cumsum)
        var = Variable(
            cumulative_col_name, variables[col].unit, f"{col} (cumulative)", "float64", Aggregation.MEAN, False
        )
        variables[var.name] = var


def _read_main_table(
    path: Path, metadata: dict, animals: dict[str, Animal]
) -> tuple[pd.DataFrame, dict[str, Variable], pd.Timedelta]:
    metadata = metadata["main_table"]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    variables: dict[str, Variable] = {}
    dtypes = {}
    for item in metadata["columns"].values():
        variable = Variable(item["id"], item["unit"], item["description"], item["type"], Aggregation.MEAN, False)
        variables[variable.name] = variable
        dtypes[variable.name] = item["type"]
    # Ignore the time for "DateTime" column
    dtypes.pop("DateTime")

    # Drop core (default) variables from the list
    variables.pop("DateTime")
    variables.pop("Animal")
    variables.pop("Box")

    # Read measurements data
    df = pd.DataFrame()
    with sqlite3.connect(path, check_same_thread=False) as connection:
        for chunk in pd.read_sql_query(
            "SELECT * FROM main_table",
            connection,
            dtype=dtypes,
            chunksize=CHUNK_SIZE,
        ):
            df = pd.concat([df, chunk], ignore_index=True)

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns")

    # Convert animal id to string first
    df["Animal"] = df["Animal"].astype(str)

    # Convert to categorical types
    df = df.astype({
        "Animal": "category",
    })

    # Sort dataframe
    df.sort_values(by=["DateTime", "Box"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Calculate cumulative values
    _add_cumulative_columns(df, "Drink", variables)
    _add_cumulative_columns(df, "Feed", variables)

    # Add Timedelta and Bin columns
    start_date_time = df.iloc[0]["DateTime"]
    df.insert(loc=1, column="Timedelta", value=df["DateTime"] - start_date_time)
    df.insert(loc=2, column="Bin", value=(df["Timedelta"] / sample_interval).round().astype(int))

    # Add Run column
    df.insert(loc=5, column="Run", value=1)

    # Add Weight variable
    variables["Weight"] = Variable("Weight", "g", "Animal weight", "float64", Aggregation.MEAN, False)

    # Add Weight column
    if "Weight" not in df.columns:
        df.insert(loc=6, column="Weight", value=df["Animal"])
        weights = {}
        for animal in animals.values():
            weights[animal.id] = animal.weight
        df = df.replace({"Weight": weights})

    # convert categorical types
    df = df.astype({
        "Weight": "float64",
    })

    # Sort variables by name
    variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

    return df, variables, sample_interval


def _read_actimot_raw(path: Path, metadata: dict, dataset: Dataset) -> ActimotDetails:
    metadata = metadata[ACTIMOT_RAW_TABLE]

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
            f"SELECT * FROM {ACTIMOT_RAW_TABLE}",
            connection,
            dtype=dtypes,
            chunksize=CHUNK_SIZE,
        ):
            chunk["X"] = np.left_shift(chunk["X2"].to_numpy(dtype=np.uint64), 32) + chunk["X1"].to_numpy(
                dtype=np.uint64
            )
            chunk.rename(columns={"Y1": "Y"}, inplace=True)
            chunk.drop(columns=["X1", "X2"], inplace=True)
            df = pd.concat([df, chunk], ignore_index=True)

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns")

    actimot_details = ActimotDetails(
        dataset,
        f"{ACTIMOT_RAW_TABLE} [sampling: {str(sample_interval)}]",
        str(path),
        variables,
        df,
        sample_interval,
    )

    return actimot_details


def _read_drinkfeed_bin(path: Path, metadata: dict, dataset: Dataset) -> MealDetails:
    metadata = metadata[DRINKFEED_BIN_TABLE]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    skipped_variables = ["DateTime", "Box"]
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
            f"SELECT * FROM {DRINKFEED_BIN_TABLE}",
            connection,
            dtype=dtypes,
            chunksize=CHUNK_SIZE,
        ):
            df = pd.concat([df, chunk], ignore_index=True)

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns")

    # Add Animal column
    box_to_animal_map = {}
    for animal in dataset.animals.values():
        box_to_animal_map[animal.box] = animal.id
    df["Animal"] = df["Box"].replace(box_to_animal_map)
    df = df.astype({
        "Animal": "category",
    })

    meal_details = MealDetails(
        dataset,
        f"{DRINKFEED_BIN_TABLE} [sampling: {str(sample_interval)}]",
        str(path),
        variables,
        df,
        sample_interval,
    )

    return meal_details


def _read_calo_bin(path: Path, metadata: dict, dataset: Dataset) -> CaloDetails:
    metadata = metadata[CALO_BIN_TABLE]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    skipped_variables = ["DateTime", "Box"]
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
            f"SELECT * FROM {CALO_BIN_TABLE}",
            connection,
            dtype=dtypes,
            chunksize=CHUNK_SIZE,
        ):
            df = pd.concat([df, chunk], ignore_index=True)

    # Convert DateTime from POSIX format
    df["DateTime"] = pd.to_datetime(df["DateTime"], origin="unix", unit="ns")

    # Sort dataframe
    df.sort_values(["Box", "DateTime"], inplace=True)

    # Assign bins
    previous_timestamp = None
    previous_box = None
    bins = []
    offsets = []
    timedeltas = []
    time_gap = timedelta(seconds=10)
    offset = 0
    for row in df.itertuples():
        timestamp = row.DateTime
        box = row.Box

        if box != previous_box:
            start_timestamp = timestamp

        if previous_timestamp is None:
            bins = [0]
        elif timestamp - previous_timestamp > time_gap:
            bin_number = bins[-1]
            bin_number = bin_number + 1

            offset = 0

            # reset bin number for a new box
            if box != previous_box:
                bin_number = 0

            bins.append(bin_number)
            start_timestamp = timestamp
        else:
            bin_number = bins[-1]

            # reset bin number for a new box
            if box != previous_box:
                bin_number = 0
                offset = 0

            bins.append(bin_number)

        if box != previous_box:
            previous_box = box

        td = timestamp - start_timestamp
        timedeltas.append(td)

        # offset = td.total_seconds()
        offsets.append(offset)
        offset = offset + 1
        previous_timestamp = timestamp

    df.insert(1, "Timedelta", timedeltas)
    df.insert(2, "Bin", bins)
    df.insert(3, "Offset", offsets)

    calo_details = CaloDetails(
        dataset,
        f"{CALO_BIN_TABLE} [sampling: {str(sample_interval)}]",
        str(path),
        variables,
        df,
        sample_interval,
    )

    return calo_details
