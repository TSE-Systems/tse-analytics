import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from tse_analytics.core.data.shared import Animal, Factor, Variable, Aggregation
from tse_analytics.core.tse_import_settings import TseImportSettings
from tse_analytics.modules.phenomaster.actimot.data.actimot_details import ActimotDetails
from tse_analytics.modules.phenomaster.data.dataset import Dataset

CHUNK_SIZE = 1000000


def load_tse_dataset(path: Path, import_settings: TseImportSettings) -> Dataset | None:
    metadata = _read_metadata(path)
    animals = _get_animals(metadata["animals"])
    # factors = TseDatasetLoader._get_factors(metadata["groups"])

    main_table_df, main_table_vars, main_table_sampling_interval = _read_main_table(path, metadata["tables"], animals)

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
    if import_settings.import_actimot:
        if "actimot_raw" in metadata["tables"]:
            actimot_details = _read_actimot_raw(path, metadata["tables"], dataset)
            dataset.actimot_details = actimot_details

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
    metadata = metadata["actimot_raw"]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    dtypes = {}
    for item in metadata["columns"].values():
        variable = Variable(item["id"], item["unit"], item["description"], item["type"], Aggregation.MEAN, False)
        dtypes[variable.name] = item["type"]
    # Ignore the time for "DateTime" column
    dtypes.pop("DateTime")

    # Read measurements data
    df = pd.DataFrame()
    with sqlite3.connect(path, check_same_thread=False) as connection:
        for chunk in pd.read_sql_query(
            "SELECT * FROM actimot_raw",
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

    variables: dict[str, Variable] = {}

    actimot_details = ActimotDetails(
        dataset,
        f"ActiMot [sampling: {str(sample_interval)}]",
        str(path),
        variables,
        df,
        sample_interval,
    )

    return actimot_details
