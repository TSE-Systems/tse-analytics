"""DuckDB-based workspace persistence.

Provides save/load functions that store a Workspace as a single DuckDB file.
Each Datatable DataFrame becomes a separate DuckDB table; all metadata is
stored in relational ``_meta_*`` tables.
"""

from __future__ import annotations

import importlib
import json
import timeit
from pathlib import Path
from typing import Any
from uuid import UUID

import duckdb
import pandas as pd
from loguru import logger

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings, OutliersType
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.workspace import Workspace

_SCHEMA_VERSION = 1

# ---------------------------------------------------------------------------
# JSON helpers for types that stdlib json cannot handle
# ---------------------------------------------------------------------------

_NULLABLE_INT_DTYPES = frozenset({
    "UInt8",
    "UInt16",
    "UInt32",
    "UInt64",
    "Int8",
    "Int16",
    "Int32",
    "Int64",
})

_EXTENSION_DTYPES = _NULLABLE_INT_DTYPES | frozenset({
    "Float32",
    "Float64",
    "boolean",
    "string",
})


def _json_default(obj: object) -> object:
    if isinstance(obj, pd.Timedelta):
        return {"__type__": "pd.Timedelta", "nanoseconds": int(obj.as_unit("ns").value)}
    if isinstance(obj, pd.Timestamp):
        return {"__type__": "pd.Timestamp", "isoformat": obj.isoformat()}
    raise TypeError(f"Cannot JSON-serialize {type(obj)}")


def _json_object_hook(d: dict) -> Any:
    t = d.get("__type__")
    if t == "pd.Timedelta":
        return pd.Timedelta(nanoseconds=d["nanoseconds"])
    if t == "pd.Timestamp":
        return pd.Timestamp(d["isoformat"])
    return d


def _dumps(obj: object) -> str:
    return json.dumps(obj, default=_json_default, ensure_ascii=False)


def _loads(s: str) -> Any:
    return json.loads(s, object_hook=_json_object_hook)


# ---------------------------------------------------------------------------
# Dynamic class import
# ---------------------------------------------------------------------------


def _class_fqn(obj: object) -> str:
    cls = type(obj)
    return f"{cls.__module__}.{cls.__qualname__}"


def _import_class(fqn: str) -> type:
    module_path, class_name = fqn.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


# ---------------------------------------------------------------------------
# DuckDB table naming
# ---------------------------------------------------------------------------


def _short_id(uuid: UUID) -> str:
    # Get last 12 symbols of hex representation of UUID
    return uuid.hex[-12:]


def _df_table_name(datatable: Datatable) -> str:
    return f"df__{datatable.name}__{_short_id(datatable.dataset.id)}__{_short_id(datatable.id)}"


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

_META_TABLES_DDL = [
    """
    CREATE TABLE _meta_workspace (
        id              UUID NOT NULL,
        name            VARCHAR NOT NULL,
        description     VARCHAR,
        metadata        JSON,
        schema_version  UINTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE _meta_datasets (
        id                UUID NOT NULL,
        name              VARCHAR NOT NULL,
        description       VARCHAR,
        dataset_class     VARCHAR NOT NULL,
        animals           JSON NOT NULL,
        factors           JSON NOT NULL,
        binning_settings  JSON NOT NULL,
        metadata          JSON
    )
    """,
    """
    CREATE TABLE reports (
        dataset_id      UUID NOT NULL,
        report_name     VARCHAR NOT NULL,
        content         VARCHAR,
        timestamp       TIMESTAMP NOT NULL
    )
    """,
    """
    CREATE TABLE _meta_datatables (
        id                      UUID NOT NULL,
        dataset_id              UUID NOT NULL,
        name                    VARCHAR NOT NULL,
        description             VARCHAR,
        duckdb_table_name       VARCHAR NOT NULL,
        variables               JSON NOT NULL,
        metadata                JSON,
        parent_datatable_id     UUID,
        outliers_settings       JSON NOT NULL
    )
    """,
    """
    CREATE TABLE _meta_raw_datatables (
        id                      UUID NOT NULL,
        dataset_id              UUID NOT NULL,
        name                    VARCHAR NOT NULL,
        description             VARCHAR,
        duckdb_table_name       VARCHAR NOT NULL,
        variables               JSON NOT NULL,
        metadata                JSON,
        extension_name          VARCHAR,
        outliers_settings       JSON NOT NULL
    )
    """,
]


def _create_meta_tables(con: duckdb.DuckDBPyConnection) -> None:
    for ddl in _META_TABLES_DDL:
        con.execute(ddl)


# ---------------------------------------------------------------------------
# DataFrame save / load helpers
# ---------------------------------------------------------------------------


def _save_dataframe(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    df: pd.DataFrame,
) -> None:
    """Write a DataFrame as a DuckDB table and record column dtypes."""
    if df.empty:
        # For empty DataFrames, create the table with proper schema
        con.execute(f'CREATE TABLE "{table_name}" AS SELECT * FROM df WHERE 1=0')
        return

    con.execute(f'CREATE TABLE "{table_name}" AS SELECT * FROM df')


def _load_dataframe(con: duckdb.DuckDBPyConnection, table_name: str, owner_id: str) -> pd.DataFrame:
    """Read a DuckDB table back into a DataFrame with original dtypes restored."""
    df = con.execute(f'SELECT * FROM "{table_name}"').fetchdf()

    rows = con.execute(
        "SELECT column_name, pandas_dtype, category_values_json FROM _meta_column_dtypes WHERE datatable_id = ?",
        [owner_id],
    ).fetchall()

    for col_name, pandas_dtype, cat_json in rows:
        if col_name not in df.columns:
            continue

        if pandas_dtype == "category":
            categories = json.loads(cat_json, object_hook=_json_object_hook) if cat_json else None
            # Replace DuckDB None / "None" string with proper NA before converting
            df[col_name] = pd.Categorical(df[col_name], categories=categories, ordered=False)
        elif "timedelta" in pandas_dtype:
            df[col_name] = pd.to_timedelta(df[col_name], unit="ns")
        elif pandas_dtype in _EXTENSION_DTYPES:
            df[col_name] = df[col_name].astype(pandas_dtype)
        elif "datetime64" in pandas_dtype and pandas_dtype != str(df[col_name].dtype):
            try:
                df[col_name] = df[col_name].astype(pandas_dtype)
            except TypeError, ValueError:
                pass

    return df


# ---------------------------------------------------------------------------
# Save implementation
# ---------------------------------------------------------------------------


def _save_workspace(con: duckdb.DuckDBPyConnection, workspace: Workspace) -> None:
    con.execute(
        "INSERT INTO _meta_workspace VALUES (?, ?, ?, ?, ?)",
        [
            workspace.id,
            workspace.name,
            workspace.description,
            _dumps(workspace.metadata),
            _SCHEMA_VERSION,
        ],
    )


def _save_reports(con: duckdb.DuckDBPyConnection, dataset_id: UUID, reports: dict[str, Report]) -> None:
    for report in reports.values():
        con.execute(
            "INSERT INTO _meta_reports VALUES (?, ?, ?, ?)",
            [
                dataset_id,
                report.name,
                report.content,
                report.timestamp,
            ],
        )


def _save_datatable(
    con: duckdb.DuckDBPyConnection,
    datatable: Datatable,
    parent_id: UUID | None = None,
) -> None:
    table_name = _df_table_name(datatable)

    _save_dataframe(con, table_name, datatable.df)

    variables_json = {}
    for variable in datatable.variables.values():
        variables_json[variable.name] = variable.get_dict()

    outliers_settings_json = {}

    con.execute(
        "INSERT INTO _meta_datatables VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            datatable.id,
            datatable.dataset.id,
            datatable.name,
            datatable.description,
            table_name,
            variables_json,
            datatable.metadata,
            parent_id,
            outliers_settings_json,
        ],
    )

    for derived in datatable.derived_tables.values():
        _save_datatable(con, derived, parent_id=datatable.id)


def _save_raw_datatable(
    con: duckdb.DuckDBPyConnection,
    datatable: Datatable,
    extension_name: str | None = None,
) -> None:
    table_name = _df_table_name(datatable)

    _save_dataframe(con, table_name, datatable.df)

    variables_json = {}
    for variable in datatable.variables.values():
        variables_json[variable.name] = variable.get_dict()

    outliers_settings_json = {}

    con.execute(
        "INSERT INTO _meta_raw_datatables VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            datatable.id,
            datatable.dataset.id,
            datatable.name,
            datatable.description,
            table_name,
            variables_json,
            datatable.metadata,
            extension_name,
            outliers_settings_json,
        ],
    )


def _save_dataset(con: duckdb.DuckDBPyConnection, dataset: Dataset) -> None:
    animals_json = {}
    for animal in dataset.animals.values():
        animals_json[animal.id] = animal.get_dict()

    factors_json = {}
    binning_settings_json = {}

    con.execute(
        "INSERT INTO _meta_datasets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            dataset.id,
            dataset.name,
            dataset.description,
            _class_fqn(dataset),
            animals_json,
            factors_json,
            binning_settings_json,
            dataset.metadata,
        ],
    )

    _save_reports(con, dataset.id, dataset.reports)

    for datatable in dataset.datatables.values():
        _save_datatable(con, datatable)

    for extension_name, extension_data in dataset.raw_datatables.items():
        for raw_datatable in extension_data.values():
            _save_raw_datatable(con, raw_datatable, extension_name)


def save_workspace(filename: str, workspace: Workspace) -> None:
    """Save a Workspace to a DuckDB file.

    Args:
        filename: Destination file path.
        workspace: The workspace to persist.
    """
    path = Path(filename)
    if path.exists():
        path.unlink()

    logger.info(f"Saving workspace to {path}")

    tic = timeit.default_timer()
    con = duckdb.connect(path)
    try:
        _create_meta_tables(con)
        _save_workspace(con, workspace)
        for dataset in workspace.datasets.values():
            _save_dataset(con, dataset)
    finally:
        con.close()

    logger.info(f"Workspace saved successfully in {(timeit.default_timer() - tic):.3f} sec")


# ---------------------------------------------------------------------------
# Load implementation
# ---------------------------------------------------------------------------


def _load_workspace_meta(con: duckdb.DuckDBPyConnection) -> Workspace:
    row = con.execute("SELECT * FROM _meta_workspace").fetchone()
    ws = Workspace(
        id=row[0],
        name=row[1],
        description=row[2],
        metadata=row[3],
    )
    return ws


def _load_reports(con: duckdb.DuckDBPyConnection, dataset_id: str, dataset: Dataset) -> dict[str, Report]:
    rows = con.execute(
        "SELECT report_name, content, timestamp FROM _meta_reports WHERE dataset_id = ?",
        [dataset_id],
    ).fetchall()
    reports: dict[str, Report] = {}
    for name, content, timestamp in rows:
        reports[name] = Report(dataset=dataset, name=name, content=content, timestamp=timestamp)
    return reports


def _load_datatables_for_dataset(
    con: duckdb.DuckDBPyConnection,
    dataset: Dataset,
) -> dict[str, Datatable]:
    """Load all non-extension datatables for a dataset and wire the tree."""
    rows = con.execute(
        "SELECT id, name, description, duckdb_table_name, metadata_json, parent_datatable_id, "
        "outliers_mode, outliers_type, iqr_multiplier, "
        "min_threshold_enabled, min_threshold, max_threshold_enabled, max_threshold "
        "FROM _meta_datatables WHERE dataset_id = ? AND extension_key IS NULL",
        [str(dataset.id)],
    ).fetchall()

    all_tables: dict[str, Datatable] = {}  # keyed by datatable id string

    for (
        dt_id,
        name,
        desc,
        tbl_name,
        meta_json,
        parent_id,
        o_mode,
        o_type,
        o_iqr,
        o_min_en,
        o_min,
        o_max_en,
        o_max,
    ) in rows:
        variables = _load_variables(con, dt_id)
        df = _load_dataframe(con, tbl_name, dt_id)
        metadata = _loads(meta_json)

        dt = Datatable(
            dataset=dataset,
            name=name,
            description=desc,
            variables=variables,
            df=df,
            metadata=metadata,
        )
        # Restore the original UUID
        dt.id = UUID(dt_id)
        dt.outliers_settings = OutliersSettings(
            mode=OutliersMode(o_mode),
            type=OutliersType(o_type),
            iqr_multiplier=o_iqr,
            min_threshold_enabled=o_min_en,
            min_threshold=o_min,
            max_threshold_enabled=o_max_en,
            max_threshold=o_max,
        )
        dt._parent_id_tmp = parent_id  # type: ignore[attr-defined]
        all_tables[dt_id] = dt

    # Wire parent/child relationships
    for dt in all_tables.values():
        parent_id = dt._parent_id_tmp  # type: ignore[attr-defined]
        del dt._parent_id_tmp  # type: ignore[attr-defined]
        if parent_id is not None and parent_id in all_tables:
            parent = all_tables[parent_id]
            dt.parent_table = parent
            parent.derived_tables[dt.name] = dt

    return {dt.name: dt for dt in all_tables.values() if dt.parent_table is None}


def _load_dataset(con: duckdb.DuckDBPyConnection, ds_id: str, ds_class_fqn: str, meta_json: str) -> Dataset:
    data = _loads(meta_json)
    metadata = data["metadata"]

    ds_cls = _import_class(ds_class_fqn)

    dataset = ds_cls(metadata=metadata, animals=animals)

    dataset.id = UUID(ds_id)
    dataset.factors = _load_factors(con, ds_id)
    dataset.binning_settings = _load_binning_settings(con, ds_id)
    dataset.reports = _load_reports(con, ds_id, dataset)
    dataset.datatables = _load_datatables_for_dataset(con, dataset)

    return dataset


def load_workspace(path: str) -> Workspace:
    """Load a Workspace from a DuckDB file.

    Args:
        path: Path to the DuckDB file.

    Returns:
        The reconstructed Workspace.
    """
    logger.info(f"Loading workspace from {path}")

    tic = timeit.default_timer()
    con = duckdb.connect(path, read_only=True)
    try:
        workspace = _load_workspace_meta(con)

        dataset_rows = con.execute("SELECT id, dataset_class, metadata FROM _meta_datasets").fetchall()
        for id, dataset_class, metadata in dataset_rows:
            dataset = _load_dataset(con, id, dataset_class, metadata)
            workspace.datasets[dataset.id] = dataset
    finally:
        con.close()

    logger.info(f"Workspace loaded successfully in {(timeit.default_timer() - tic):.3f} sec")

    return workspace
