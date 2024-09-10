import json
import sqlite3

import pandas as pd
import polars as pl
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from tse_analytics.core.data.shared import Animal, Factor, Variable
from tse_analytics.modules.phenomaster.actimot.data.actimot_details import ActimotDetails
from tse_analytics.modules.phenomaster.data.dataset import Dataset

DELPHI_EPOCH = datetime(1899, 12, 30)
CHUNK_SIZE = 1000000


def import_tse_dataset(path: Path) -> Dataset | None:
    metadata = _read_metadata(path)
    animals = _get_animals(metadata["animals"])
    # factors = _get_factors(metadata["groups"])

    main_table_df, main_table_vars, main_table_sampling_interval = _read_main_table(
        path, metadata["tables"], animals
    )

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
    if "actimot_raw" in metadata["tables"]:
        actimot_details = _read_actimot_raw(path, metadata["tables"], dataset)
        dataset.actimot_details = actimot_details

    return dataset


def _read_metadata(path: Path) -> dict:
    df = pl.read_database_uri(
        query="SELECT * FROM metadata",
        uri=f"sqlite:///{path}"
    )
    metadata_str = df.item(0, "json")
    metadata = json.loads(metadata_str)

    # Convert time intervals from [ms] to Timedeltas
    metadata["experiment"]["runtime"] = str(pd.to_timedelta(metadata["experiment"]["runtime"], unit="ms"))
    metadata["experiment"]["cycle_interval"] = str(
        pd.to_timedelta(metadata["experiment"]["cycle_interval"], unit="ms")
    )

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


def _add_cumulative_columns(df: pl.DataFrame, origin_name: str, variables: dict[str, Variable]):
    cols = [col for col in df.columns if origin_name in col]
    for col in cols:
        cumulative_col_name = col + "C"
        df[cumulative_col_name] = df.groupby("Box", observed=False)[col].transform(pd.Series.cumsum)
        var = Variable(
            name=cumulative_col_name, unit=variables[col].unit, description=f"{col} (cumulative)", type="float64"
        )
        variables[var.name] = var


def _read_main_table(
    path: Path, metadata: dict, animals: dict[str, Animal]
) -> tuple[pl.DataFrame, dict[str, Variable], pd.Timedelta]:
    metadata = metadata["main_table"]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    variables: dict[str, Variable] = {}
    dtypes = {}
    for item in metadata["columns"].values():
        variable = Variable(
            name=item["id"],
            unit=item["unit"],
            description=item["description"],
            type=item["type"],
        )
        variables[variable.name] = variable
        dtypes[variable.name] = item["type"]
    # Ignore the time for "DateTime" column
    dtypes.pop("DateTime")

    # Drop core (default) variables from the list
    variables.pop("DateTime")
    variables.pop("Animal")
    variables.pop("Box")

    # Read measurements data
    df = pl.read_database_uri(
        query="SELECT * FROM main_table",
        uri=f"sqlite:///{path}"
    )

    df = df.with_columns(
        (pl.from_epoch((pl.col("DateTime") - 25569) * 86400000000, time_unit="us"))
    )

    # Convert animal id to string first
    df = df.cast({
        "Animal": pl.Utf8,
    }).cast({
        "Animal": pl.Categorical,
    })

    # Sort dataframe
    df = df.sort(["DateTime", "Box"], descending=False)

    # Calculate cumulative values
    # _add_cumulative_columns(df, "Drink", variables)
    # _add_cumulative_columns(df, "Feed", variables)

    # Add Timedelta and Bin columns
    start_date_time = df.item(0, "DateTime")
    df.insert_column(1, pl.Series("Timedelta", df["DateTime"] - start_date_time))
    df.insert_column(2, pl.Series("Bin", df.select(pl.col("Timedelta") / sample_interval.to_pytimedelta()).cast(pl.UInt64)))

    # Add Run column
    # df = df.with_columns(pl.lit(1, dtype=pl.UInt8).alias("Run"))
    df.insert_column(5, pl.Series("Run", pl.repeat(1, len(df), dtype=pl.UInt8, eager=True)))

    # Add Weight variable
    variables["Weight"] = Variable(name="Weight", unit="g", description="Animal weight", type="float64")

    # Add Weight column
    if "Weight" not in df.columns:
        df.insert_column(6, pl.Series("Weight", df["Animal"]))
        weights = {}
        for animal in animals.values():
            weights[animal.id] = animal.weight
        df = df.with_columns(pl.col("Weight").replace(weights))

    # Sort variables by name
    variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

    return df, variables, sample_interval


def _read_actimot_raw(path: Path, metadata: dict, dataset: Dataset) -> ActimotDetails:
    metadata = metadata["actimot_raw"]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    # Read variables list
    dtypes = {}
    for item in metadata["columns"].values():
        variable = Variable(
            name=item["id"],
            unit=item["unit"],
            description=item["description"],
            type=item["type"],
        )
        dtypes[variable.name] = item["type"]
    # Ignore the time for "DateTime" column
    dtypes.pop("DateTime")

    # Read measurements data
    df = pl.read_database_uri(
        query="SELECT * FROM actimot_raw",
        uri=f"sqlite:///{path}"
    )

    df = df.with_columns(
        (pl.from_epoch((pl.col("DateTime") - 25569) * 86400000000, time_unit="us")),
        (np.left_shift(pl.col("X2").cast(pl.UInt64), 32) + pl.col("X1").cast(pl.UInt64)).alias("X")
    )

    df = df.rename({"Y1": "Y"})
    df = df.drop(["X1", "X2"])

    variables: dict[str, Variable] = {}

    actimot_details = ActimotDetails(
        dataset,
        f"ActiMot Details [Interval: {str(sample_interval)}]",
        str(path),
        variables,
        df,
        sample_interval,
    )

    return actimot_details
