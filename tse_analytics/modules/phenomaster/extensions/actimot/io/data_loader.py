from pathlib import Path

import connectorx as cx
import numpy as np
import pandas as pd
import pyarrow as pa

from tse_analytics.core.csv_import_settings import CsvImportSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.io import tse_import_settings


def read_actimot_raw(path: Path, dataset: PhenoMasterDataset) -> Datatable:
    metadata = dataset.metadata["tables"][tse_import_settings.ACTIMOT_RAW_TABLE]

    sample_interval = pd.Timedelta(metadata["sample_interval"])

    df = cx.read_sql(
        f"sqlite:///{path}",
        f"SELECT DateTime, Box, X1, X2, Y1 AS Y FROM {tse_import_settings.ACTIMOT_RAW_TABLE}",
        return_type="pandas",
    )

    # Convert types
    df = df.astype({"Box": "uint16[pyarrow]"}, errors="ignore")

    df["X"] = np.left_shift(df["X2"].to_numpy(dtype=np.uint64), 32) + df["X1"].to_numpy(dtype=np.uint64)
    df = df.drop(columns=["X1", "X2"])

    # Convert DateTime from POSIX format
    df["DateTime"] = (
        pd
        .to_datetime(df["DateTime"], origin="unix", unit="ns")
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    box_to_animal_map = {animal.properties["Box"]: animal.id for animal in dataset.animals.values()}
    df.insert(
        df.columns.get_loc("Box"),
        "Animal",
        df["Box"].map(box_to_animal_map),
    )

    # Convert categorical types
    df = df.astype({
        "Animal": "category",
        "Box": "category",
    })

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    raw_datatable = Datatable(
        dataset,
        tse_import_settings.ACTIMOT_RAW_TABLE,
        f"Raw {tse_import_settings.ACTIMOT_RAW_TABLE} datatable",
        {},
        df,
        {
            "origin_path": str(path),
            "sampling_interval": sample_interval,
        },
    )

    return raw_datatable


def import_actimot_csv_data(
    filename: str,
    dataset: PhenoMasterDataset,
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
        datetime_column_header: "string[pyarrow]",
        "Rel. [s]": "float64[pyarrow]",
        "BoxNr": "uint16[pyarrow]",
        "X (cm)": "float64[pyarrow]",
        "Y (cm)": "float64[pyarrow]",
        "X": "string[pyarrow]",
        "Y": "string[pyarrow]",
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
        dtype_backend="pyarrow",
        na_values=["-"],
    )

    # Rename table columns
    df.rename(columns={datetime_column_header: "DateTime", "BoxNr": "Box"}, inplace=True)

    # Convert DateTime column
    df["DateTime"] = (
        pd
        .to_datetime(
            df["DateTime"],
            format=csv_import_settings.datetime_format if csv_import_settings.use_datetime_format else "mixed",
            dayfirst=csv_import_settings.day_first,
        )
        .dt.as_unit(TIME_RESOLUTION_UNIT)
        .astype(pd.ArrowDtype(pa.timestamp(unit=TIME_RESOLUTION_UNIT)))
    )

    box_to_animal_map = {}
    for animal in dataset.animals.values():
        box_to_animal_map[animal.properties["Box"]] = animal.id

    df.insert(
        df.columns.get_loc("Box") + 1,
        "Animal",
        None,
    )

    df["Animal"] = df["Box"].astype("int16[pyarrow]")
    df.replace({"Animal": box_to_animal_map}, inplace=True)

    df = df.sort_values(["Box", "DateTime"])
    df.reset_index(drop=True, inplace=True)

    # convert categorical types
    df = df.astype({
        "Animal": "category",
    })

    # Sampling interval
    sampling_interval = df.iloc[1].at["DateTime"] - df.iloc[0].at["DateTime"]

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

    raw_datatable = Datatable(
        dataset,
        tse_import_settings.ACTIMOT_RAW_TABLE,
        f"Raw {tse_import_settings.ACTIMOT_RAW_TABLE} datatable",
        {},
        df,
        {
            "origin_path": str(path),
            "sampling_interval": sampling_interval,
        },
    )

    return raw_datatable
