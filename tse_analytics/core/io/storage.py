"""DuckDB-based workspace persistence.

Provides save/load functions that store a Workspace as a single DuckDB file.
Each Datatable DataFrame becomes a separate DuckDB table; all metadata is
stored in relational ``_meta_*`` tables.
"""

from __future__ import annotations

import timeit
from pathlib import Path
from typing import Any
from uuid import UUID

import duckdb
import pandas as pd
from loguru import logger
from pydantic import TypeAdapter

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.outliers import OutliersSettings
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import Animal, Factor, Variable
from tse_analytics.core.data.workspace import Workspace

_SCHEMA_VERSION = 1


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
        dataset_type      VARCHAR NOT NULL,
        animals           JSON NOT NULL,
        factors           JSON NOT NULL,
        metadata          JSON
    )
    """,
    """
    CREATE TABLE _meta_reports (
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
        parent_datatable_id     UUID,
        name                    VARCHAR NOT NULL,
        description             VARCHAR,
        duckdb_table_name       VARCHAR NOT NULL,
        variables               JSON NOT NULL,
        metadata                JSON,
        outliers_settings       JSON NOT NULL
    )
    """,
    """
    CREATE TABLE _meta_raw_datatables (
        id                      UUID NOT NULL,
        dataset_id              UUID NOT NULL,
        extension_name          VARCHAR NOT NULL,
        name                    VARCHAR NOT NULL,
        description             VARCHAR,
        duckdb_table_name       VARCHAR NOT NULL,
        variables               JSON NOT NULL,
        metadata                JSON,
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


def _load_dataframe(con: duckdb.DuckDBPyConnection, table_name: str) -> pd.DataFrame:
    """Read a DuckDB table back into a DataFrame with original dtypes restored."""
    df = con.execute(f'SELECT * FROM "{table_name}"').fetchdf()

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
            workspace.metadata,
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

    con.execute(
        "INSERT INTO _meta_datatables VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            datatable.id,
            datatable.dataset.id,
            parent_id,
            datatable.name,
            datatable.description,
            table_name,
            TypeAdapter(dict[str, Variable]).dump_python(datatable.variables),
            datatable.metadata,
            TypeAdapter(OutliersSettings).dump_python(datatable.outliers_settings),
        ],
    )


def _save_raw_datatable(
    con: duckdb.DuckDBPyConnection,
    datatable: Datatable,
    extension_name: str | None = None,
) -> None:
    table_name = _df_table_name(datatable)

    _save_dataframe(con, table_name, datatable.df)

    con.execute(
        "INSERT INTO _meta_raw_datatables VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            datatable.id,
            datatable.dataset.id,
            extension_name,
            datatable.name,
            datatable.description,
            table_name,
            TypeAdapter(dict[str, Variable]).dump_python(datatable.variables),
            datatable.metadata,
            TypeAdapter(OutliersSettings).dump_python(datatable.outliers_settings),
        ],
    )


def _save_dataset(con: duckdb.DuckDBPyConnection, dataset: Dataset) -> None:
    con.execute(
        "INSERT INTO _meta_datasets VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            dataset.id,
            dataset.name,
            dataset.description,
            dataset.dataset_type,
            TypeAdapter(dict[str, Animal]).dump_python(dataset.animals),
            TypeAdapter(dict[str, Factor]).dump_python(dataset.factors),
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
        row[0],
        row[1],
        row[2],
        TypeAdapter(dict[str, Any]).validate_json(row[3]),
    )
    return ws


def _load_reports(con: duckdb.DuckDBPyConnection, dataset_id: UUID, dataset: Dataset) -> dict[str, Report]:
    rows = con.execute(
        "SELECT report_name, content, timestamp FROM _meta_reports WHERE dataset_id = ?",
        [dataset_id],
    ).fetchall()
    reports: dict[str, Report] = {}
    for name, content, timestamp in rows:
        reports[name] = Report(
            dataset,
            name,
            content,
            timestamp,
        )
    return reports


def _load_datatables_for_dataset(
    con: duckdb.DuckDBPyConnection,
    dataset: Dataset,
) -> dict[str, Datatable]:
    """Load all non-extension datatables for a dataset and wire the tree."""
    rows = con.execute(
        "SELECT id, parent_datatable_id, name, description, duckdb_table_name, variables, metadata, outliers_settings "
        "FROM _meta_datatables WHERE dataset_id = ?",
        [dataset.id],
    ).fetchall()

    datatables: dict[str, Datatable] = {}  # keyed by datatable id string

    for (
        datatable_id,
        parent_datatable_id,
        name,
        description,
        duckdb_table_name,
        variables_json,
        metadata,
        outliers_settings,
    ) in rows:
        df = _load_dataframe(con, duckdb_table_name)

        datatable = Datatable(
            dataset,
            name,
            description,
            TypeAdapter(dict[str, Variable]).validate_json(variables_json),
            df,
            TypeAdapter(dict[str, Any]).validate_json(metadata),
        )
        datatable.id = datatable_id
        datatable.outliers_settings = TypeAdapter(OutliersSettings).validate_json(outliers_settings)
        datatables[datatable_id] = datatable

    return {datatable.name: datatable for datatable in datatables.values()}


def _load_raw_datatables_for_dataset(
    con: duckdb.DuckDBPyConnection,
    dataset: Dataset,
) -> dict[str, dict[str, Datatable]]:
    """Load all raw extension datatables for a dataset and wire the tree."""
    rows = con.execute(
        "SELECT id, extension_name, name, description, duckdb_table_name, variables, metadata, outliers_settings "
        "FROM _meta_raw_datatables WHERE dataset_id = ?",
        [dataset.id],
    ).fetchall()

    raw_datatables: dict[str, dict[str, Datatable]] = {}

    for (
        datatable_id,
        extension_name,
        name,
        description,
        duckdb_table_name,
        variables_json,
        metadata,
        outliers_settings,
    ) in rows:
        df = _load_dataframe(con, duckdb_table_name)

        datatable = Datatable(
            dataset,
            name,
            description,
            TypeAdapter(dict[str, Variable]).validate_json(variables_json),
            df,
            TypeAdapter(dict[str, Any]).validate_json(metadata),
        )
        datatable.id = datatable_id
        datatable.outliers_settings = TypeAdapter(OutliersSettings).validate_json(outliers_settings)

        if extension_name not in raw_datatables:
            raw_datatables[extension_name] = {}

        raw_datatables[extension_name][datatable.name] = datatable

    return raw_datatables


def _load_dataset(con: duckdb.DuckDBPyConnection, dataset_id: UUID) -> Dataset:
    row = con.execute(
        "SELECT id, name, description, dataset_type, animals, factors, metadata FROM _meta_datasets WHERE id = ?",
        [dataset_id],
    ).fetchone()

    dataset = Dataset(
        row[1],
        row[2],
        row[3],
        TypeAdapter(dict[str, Any]).validate_json(row[6]),
        TypeAdapter(dict[str, Animal]).validate_json(row[4]),
    )
    dataset.id = row[0]
    dataset.factors = TypeAdapter(dict[str, Factor]).validate_json(row[5])
    dataset.reports = _load_reports(con, row[0], dataset)

    dataset.datatables = _load_datatables_for_dataset(con, dataset)
    dataset.raw_datatables = _load_raw_datatables_for_dataset(con, dataset)

    # Heal workspaces saved before the auto "Bin" factor existed: if any
    # datatable is a regular timeseries but no "Bin" factor is present,
    # re-running set_factors auto-creates and materializes one.
    has_regular = any(dt.is_regular_timeseries for dt in dataset.datatables.values())
    if has_regular and "Bin" not in dataset.factors:
        dataset.set_factors(dataset.factors)

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

        dataset_rows = con.execute("SELECT id FROM _meta_datasets").fetchall()
        for row in dataset_rows:
            dataset = _load_dataset(con, row[0])
            workspace.datasets[dataset.id] = dataset

        logger.info(f"Workspace loaded successfully in {(timeit.default_timer() - tic):.3f} sec")
    except Exception as e:
        logger.error(f"Failed to load workspace from {path}: {e}")
    finally:
        con.close()

    return workspace
