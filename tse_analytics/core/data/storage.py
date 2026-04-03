"""DuckDB-based workspace persistence.

Provides save/load functions that store a Workspace as a single DuckDB file.
Each Datatable DataFrame becomes a separate DuckDB table; all metadata is
stored in relational ``_meta_*`` tables.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any
from uuid import UUID

import duckdb
import pandas as pd
from loguru import logger

from tse_analytics.core.data.binning import (
    BinningSettings,
    TimeCyclesBinningSettings,
    TimeIntervalsBinningSettings,
    TimePhasesBinningSettings,
)
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings, OutliersType
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import Aggregation, Animal, Factor, FactorLevel, TimePhase, Variable
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
    return uuid.hex[:12]


def _df_table_name(dataset_id: UUID, datatable_id: UUID) -> str:
    return f"df__{_short_id(dataset_id)}__{_short_id(datatable_id)}"


def _ext_table_name(dataset_id: UUID, extension_key: str, data_key: str) -> str:
    safe_ext = extension_key.replace(" ", "_").replace("-", "_").lower()
    safe_key = data_key.replace(" ", "_").replace("-", "_").lower()
    return f"ext__{_short_id(dataset_id)}__{safe_ext}__{safe_key}"


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

_META_TABLES_DDL = [
    """
    CREATE TABLE _meta_workspace (
        id              VARCHAR NOT NULL,
        name            VARCHAR NOT NULL,
        description     VARCHAR NOT NULL DEFAULT '',
        metadata_json   VARCHAR NOT NULL DEFAULT '{}',
        schema_version  INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE _meta_datasets (
        id              VARCHAR NOT NULL,
        dataset_class   VARCHAR NOT NULL,
        metadata_json   VARCHAR NOT NULL
    )
    """,
    """
    CREATE TABLE _meta_animals (
        dataset_id      VARCHAR NOT NULL,
        animal_id       VARCHAR NOT NULL,
        color           VARCHAR NOT NULL,
        properties_json VARCHAR NOT NULL DEFAULT '{}'
    )
    """,
    """
    CREATE TABLE _meta_factors (
        dataset_id      VARCHAR NOT NULL,
        factor_name     VARCHAR NOT NULL
    )
    """,
    """
    CREATE TABLE _meta_factor_levels (
        dataset_id      VARCHAR NOT NULL,
        factor_name     VARCHAR NOT NULL,
        level_name      VARCHAR NOT NULL,
        color           VARCHAR NOT NULL,
        animal_ids_json VARCHAR NOT NULL DEFAULT '[]'
    )
    """,
    """
    CREATE TABLE _meta_binning_settings (
        dataset_id          VARCHAR NOT NULL,
        intervals_unit      VARCHAR NOT NULL DEFAULT 'hour',
        intervals_delta     INTEGER NOT NULL DEFAULT 1,
        cycles_light_start  VARCHAR NOT NULL DEFAULT '07:00:00',
        cycles_dark_start   VARCHAR NOT NULL DEFAULT '19:00:00',
        phases_json         VARCHAR NOT NULL DEFAULT '[]'
    )
    """,
    """
    CREATE TABLE _meta_reports (
        dataset_id      VARCHAR NOT NULL,
        report_name     VARCHAR NOT NULL,
        content         VARCHAR NOT NULL DEFAULT '',
        timestamp       TIMESTAMP NOT NULL
    )
    """,
    """
    CREATE TABLE _meta_datatables (
        id                      VARCHAR NOT NULL,
        dataset_id              VARCHAR NOT NULL,
        name                    VARCHAR NOT NULL,
        description             VARCHAR NOT NULL DEFAULT '',
        duckdb_table_name       VARCHAR NOT NULL,
        metadata_json           VARCHAR NOT NULL DEFAULT '{}',
        parent_datatable_id     VARCHAR,
        extension_key           VARCHAR,
        outliers_mode           VARCHAR NOT NULL DEFAULT 'Outliers detection off',
        outliers_type           VARCHAR NOT NULL DEFAULT 'Interquartile Range (IQR)',
        iqr_multiplier          DOUBLE  NOT NULL DEFAULT 1.5,
        min_threshold_enabled   BOOLEAN NOT NULL DEFAULT FALSE,
        min_threshold           DOUBLE  NOT NULL DEFAULT 0.0,
        max_threshold_enabled   BOOLEAN NOT NULL DEFAULT FALSE,
        max_threshold           DOUBLE  NOT NULL DEFAULT 0.0
    )
    """,
    """
    CREATE TABLE _meta_variables (
        datatable_id    VARCHAR NOT NULL,
        var_name        VARCHAR NOT NULL,
        unit            VARCHAR NOT NULL DEFAULT '',
        description     VARCHAR NOT NULL DEFAULT '',
        type            VARCHAR NOT NULL DEFAULT '',
        aggregation     VARCHAR NOT NULL DEFAULT 'mean',
        remove_outliers BOOLEAN NOT NULL DEFAULT FALSE
    )
    """,
    """
    CREATE TABLE _meta_column_dtypes (
        datatable_id        VARCHAR NOT NULL,
        column_name         VARCHAR NOT NULL,
        pandas_dtype        VARCHAR NOT NULL,
        category_values_json VARCHAR
    )
    """,
    """
    CREATE TABLE _meta_extensions (
        dataset_id      VARCHAR NOT NULL,
        extension_key   VARCHAR NOT NULL,
        extension_class VARCHAR NOT NULL,
        extension_name  VARCHAR NOT NULL,
        extra_json      VARCHAR NOT NULL DEFAULT '{}'
    )
    """,
    """
    CREATE TABLE _meta_extension_dataframes (
        dataset_id          VARCHAR NOT NULL,
        extension_key       VARCHAR NOT NULL,
        data_key            VARCHAR NOT NULL,
        duckdb_table_name   VARCHAR NOT NULL
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
    owner_id: str,
) -> None:
    """Write a DataFrame as a DuckDB table and record column dtypes."""
    if df.empty:
        # For empty DataFrames, create the table with proper schema
        con.execute(f'CREATE TABLE "{table_name}" AS SELECT * FROM df WHERE 1=0')
        for col in df.columns:
            dtype_str = str(df[col].dtype)
            cat_json = None
            if dtype_str == "category":
                cat_json = json.dumps(df[col].cat.categories.tolist(), default=_json_default, ensure_ascii=False)
            con.execute(
                "INSERT INTO _meta_column_dtypes VALUES (?, ?, ?, ?)",
                [owner_id, col, dtype_str, cat_json],
            )
        return

    prepared = df.copy()
    for col in prepared.columns:
        dtype_str = str(prepared[col].dtype)
        cat_json = None

        if dtype_str == "category":
            cat_json = json.dumps(prepared[col].cat.categories.tolist(), default=_json_default, ensure_ascii=False)
            prepared[col] = prepared[col].astype("object")
        elif "timedelta" in dtype_str:
            prepared[col] = prepared[col].astype("int64")
        elif dtype_str in _NULLABLE_INT_DTYPES:
            # Convert to regular numpy int for DuckDB compatibility, keeping NAs
            pass

        con.execute(
            "INSERT INTO _meta_column_dtypes VALUES (?, ?, ?, ?)",
            [owner_id, col, dtype_str, cat_json],
        )

    con.execute(f'CREATE TABLE "{table_name}" AS SELECT * FROM prepared')


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


def _save_workspace_meta(con: duckdb.DuckDBPyConnection, workspace: Workspace) -> None:
    con.execute(
        "INSERT INTO _meta_workspace VALUES (?, ?, ?, ?, ?)",
        [str(workspace.id), workspace.name, workspace.description, _dumps(workspace.metadata), _SCHEMA_VERSION],
    )


def _save_animals(con: duckdb.DuckDBPyConnection, dataset_id: str, animals: dict[str, Animal]) -> None:
    for animal in animals.values():
        con.execute(
            "INSERT INTO _meta_animals VALUES (?, ?, ?, ?)",
            [dataset_id, animal.id, animal.color, _dumps(animal.properties)],
        )


def _save_factors(con: duckdb.DuckDBPyConnection, dataset_id: str, factors: dict[str, Factor]) -> None:
    for factor in factors.values():
        con.execute("INSERT INTO _meta_factors VALUES (?, ?)", [dataset_id, factor.name])
        for level in factor.levels:
            con.execute(
                "INSERT INTO _meta_factor_levels VALUES (?, ?, ?, ?, ?)",
                [dataset_id, factor.name, level.name, level.color, json.dumps(level.animal_ids)],
            )


def _save_binning_settings(con: duckdb.DuckDBPyConnection, dataset_id: str, bs: BinningSettings) -> None:
    phases_json = _dumps([
        {"name": p.name, "start_timestamp_ns": int(p.start_timestamp.as_unit("ns").value)}
        for p in bs.time_phases_settings.time_phases
    ])
    con.execute(
        "INSERT INTO _meta_binning_settings VALUES (?, ?, ?, ?, ?, ?)",
        [
            dataset_id,
            bs.time_intervals_settings.unit,
            bs.time_intervals_settings.delta,
            bs.time_cycles_settings.light_cycle_start.isoformat(),
            bs.time_cycles_settings.dark_cycle_start.isoformat(),
            phases_json,
        ],
    )


def _save_reports(con: duckdb.DuckDBPyConnection, dataset_id: str, reports: dict[str, Report]) -> None:
    for report in reports.values():
        con.execute(
            "INSERT INTO _meta_reports VALUES (?, ?, ?, ?)",
            [dataset_id, report.name, report.content, report.timestamp],
        )


def _save_variables(con: duckdb.DuckDBPyConnection, datatable_id: str, variables: dict[str, Variable]) -> None:
    for var in variables.values():
        con.execute(
            "INSERT INTO _meta_variables VALUES (?, ?, ?, ?, ?, ?, ?)",
            [datatable_id, var.name, var.unit, var.description, var.type, str(var.aggregation), var.remove_outliers],
        )


def _save_datatable(
    con: duckdb.DuckDBPyConnection,
    dataset_id: UUID,
    datatable: Datatable,
    parent_id: str | None = None,
    extension_key: str | None = None,
) -> None:
    dt_id = str(datatable.id)
    table_name = _df_table_name(dataset_id, datatable.id)

    _save_dataframe(con, table_name, datatable.df, dt_id)
    _save_variables(con, dt_id, datatable.variables)

    os = datatable.outliers_settings
    con.execute(
        "INSERT INTO _meta_datatables VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            dt_id,
            str(dataset_id),
            datatable.name,
            datatable.description,
            table_name,
            _dumps(datatable.metadata),
            parent_id,
            extension_key,
            str(os.mode),
            str(os.type),
            os.iqr_multiplier,
            os.min_threshold_enabled,
            os.min_threshold,
            os.max_threshold_enabled,
            os.max_threshold,
        ],
    )

    for derived in datatable.derived_tables.values():
        _save_datatable(con, dataset_id, derived, parent_id=dt_id)


def _save_extension_phenomaster(con: duckdb.DuckDBPyConnection, dataset_id: UUID, dataset: Dataset) -> None:
    from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset

    if not isinstance(dataset, PhenoMasterDataset):
        return

    for key, ext in dataset.extensions_data.items():
        extra: dict[str, Any] = {}
        if hasattr(ext, "ref_box_mapping"):
            extra["ref_box_mapping"] = ext.ref_box_mapping
        if hasattr(ext, "animal_ids"):
            extra["animal_ids"] = ext.animal_ids

        con.execute(
            "INSERT INTO _meta_extensions VALUES (?, ?, ?, ?, ?)",
            [str(dataset_id), key, _class_fqn(ext), ext.name, _dumps(extra)],
        )

        _save_datatable(con, dataset_id, ext.raw_datatable, extension_key=key)


def _save_extension_intellicage(con: duckdb.DuckDBPyConnection, dataset_id: UUID, dataset: Dataset) -> None:
    from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset

    if not isinstance(dataset, IntelliCageDataset) or dataset.intellicage_data is None:
        return

    ic = dataset.intellicage_data
    extra = {"device_ids": ic.device_ids}
    con.execute(
        "INSERT INTO _meta_extensions VALUES (?, ?, ?, ?, ?)",
        [str(dataset_id), "intellicage_data", _class_fqn(ic), ic.name, _dumps(extra)],
    )

    for data_key, df in ic.raw_data.items():
        table_name = _ext_table_name(dataset_id, "intellicage_data", data_key)
        owner_id = f"ext_{_short_id(dataset_id)}_intellicage_data_{data_key}"
        _save_dataframe(con, table_name, df, owner_id)
        con.execute(
            "INSERT INTO _meta_extension_dataframes VALUES (?, ?, ?, ?)",
            [str(dataset_id), "intellicage_data", data_key, table_name],
        )


def _save_extension_intellimaze(con: duckdb.DuckDBPyConnection, dataset_id: UUID, dataset: Dataset) -> None:
    from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset

    if not isinstance(dataset, IntelliMazeDataset):
        return

    for key, ext in dataset.extensions_data.items():
        extra = {"device_ids": ext.device_ids}
        con.execute(
            "INSERT INTO _meta_extensions VALUES (?, ?, ?, ?, ?)",
            [str(dataset_id), key, _class_fqn(ext), ext.name, _dumps(extra)],
        )

        for data_key, df in ext.raw_data.items():
            table_name = _ext_table_name(dataset_id, key, data_key)
            owner_id = f"ext_{_short_id(dataset_id)}_{key}_{data_key}"
            _save_dataframe(con, table_name, df, owner_id)
            con.execute(
                "INSERT INTO _meta_extension_dataframes VALUES (?, ?, ?, ?)",
                [str(dataset_id), key, data_key, table_name],
            )


def _save_dataset(con: duckdb.DuckDBPyConnection, dataset: Dataset) -> None:
    ds_id = str(dataset.id)

    # Store IntelliMaze devices in metadata for reconstruction
    metadata_to_save = dataset.metadata
    extra_init: dict[str, Any] = {}
    from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset

    if isinstance(dataset, IntelliMazeDataset):
        extra_init["devices"] = dataset.devices

    con.execute(
        "INSERT INTO _meta_datasets VALUES (?, ?, ?)",
        [ds_id, _class_fqn(dataset), _dumps({"metadata": metadata_to_save, "extra_init": extra_init})],
    )

    _save_animals(con, ds_id, dataset.animals)
    _save_factors(con, ds_id, dataset.factors)
    _save_binning_settings(con, ds_id, dataset.binning_settings)
    _save_reports(con, ds_id, dataset.reports)

    for datatable in dataset.datatables.values():
        _save_datatable(con, dataset.id, datatable)

    _save_extension_phenomaster(con, dataset.id, dataset)
    _save_extension_intellicage(con, dataset.id, dataset)
    _save_extension_intellimaze(con, dataset.id, dataset)


def save_workspace(path: str, workspace: Workspace) -> None:
    """Save a Workspace to a DuckDB file.

    Args:
        path: Destination file path.
        workspace: The workspace to persist.
    """
    p = Path(path)
    if p.exists():
        p.unlink()

    logger.info("Saving workspace to {}", path)
    con = duckdb.connect(str(p))
    try:
        _create_meta_tables(con)
        _save_workspace_meta(con, workspace)
        for dataset in workspace.datasets.values():
            _save_dataset(con, dataset)
    finally:
        con.close()
    logger.info("Workspace saved successfully")


# ---------------------------------------------------------------------------
# Load implementation
# ---------------------------------------------------------------------------


def _load_workspace_meta(con: duckdb.DuckDBPyConnection) -> Workspace:
    row = con.execute("SELECT * FROM _meta_workspace").fetchone()
    ws = Workspace(
        id=UUID(row[0]),
        name=row[1],
        description=row[2],
        metadata=_loads(row[3]),
    )
    return ws


def _load_animals(con: duckdb.DuckDBPyConnection, dataset_id: str) -> dict[str, Animal]:
    rows = con.execute(
        "SELECT animal_id, color, properties_json FROM _meta_animals WHERE dataset_id = ?",
        [dataset_id],
    ).fetchall()
    animals: dict[str, Animal] = {}
    for animal_id, color, props_json in rows:
        animals[animal_id] = Animal(id=animal_id, color=color, properties=_loads(props_json))
    return animals


def _load_factors(con: duckdb.DuckDBPyConnection, dataset_id: str) -> dict[str, Factor]:
    factor_rows = con.execute(
        "SELECT factor_name FROM _meta_factors WHERE dataset_id = ?",
        [dataset_id],
    ).fetchall()
    factors: dict[str, Factor] = {}
    for (factor_name,) in factor_rows:
        level_rows = con.execute(
            "SELECT level_name, color, animal_ids_json FROM _meta_factor_levels "
            "WHERE dataset_id = ? AND factor_name = ?",
            [dataset_id, factor_name],
        ).fetchall()
        levels = [FactorLevel(name=ln, color=c, animal_ids=json.loads(aids)) for ln, c, aids in level_rows]
        factors[factor_name] = Factor(name=factor_name, levels=levels)
    return factors


def _load_binning_settings(con: duckdb.DuckDBPyConnection, dataset_id: str) -> BinningSettings:
    row = con.execute(
        "SELECT intervals_unit, intervals_delta, cycles_light_start, cycles_dark_start, phases_json "
        "FROM _meta_binning_settings WHERE dataset_id = ?",
        [dataset_id],
    ).fetchone()
    if row is None:
        return BinningSettings()

    from datetime import time

    phases_data = _loads(row[4])
    time_phases = [
        TimePhase(name=p["name"], start_timestamp=pd.Timedelta(nanoseconds=p["start_timestamp_ns"]))
        for p in phases_data
    ]

    return BinningSettings(
        time_intervals_settings=TimeIntervalsBinningSettings(unit=row[0], delta=row[1]),
        time_cycles_settings=TimeCyclesBinningSettings(
            light_cycle_start=time.fromisoformat(row[2]),
            dark_cycle_start=time.fromisoformat(row[3]),
        ),
        time_phases_settings=TimePhasesBinningSettings(time_phases=time_phases),
    )


def _load_reports(con: duckdb.DuckDBPyConnection, dataset_id: str, dataset: Dataset) -> dict[str, Report]:
    rows = con.execute(
        "SELECT report_name, content, timestamp FROM _meta_reports WHERE dataset_id = ?",
        [dataset_id],
    ).fetchall()
    reports: dict[str, Report] = {}
    for name, content, timestamp in rows:
        reports[name] = Report(dataset=dataset, name=name, content=content, timestamp=timestamp)
    return reports


def _load_variables(con: duckdb.DuckDBPyConnection, datatable_id: str) -> dict[str, Variable]:
    rows = con.execute(
        "SELECT var_name, unit, description, type, aggregation, remove_outliers "
        "FROM _meta_variables WHERE datatable_id = ?",
        [datatable_id],
    ).fetchall()
    variables: dict[str, Variable] = {}
    for var_name, unit, desc, vtype, agg, remove in rows:
        variables[var_name] = Variable(
            name=var_name,
            unit=unit,
            description=desc,
            type=vtype,
            aggregation=Aggregation(agg),
            remove_outliers=remove,
        )
    return variables


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


def _load_extension_datatable(
    con: duckdb.DuckDBPyConnection,
    dataset: Dataset,
    extension_key: str,
) -> Datatable | None:
    """Load a single extension raw_datatable."""
    row = con.execute(
        "SELECT id, name, description, duckdb_table_name, metadata_json, "
        "outliers_mode, outliers_type, iqr_multiplier, "
        "min_threshold_enabled, min_threshold, max_threshold_enabled, max_threshold "
        "FROM _meta_datatables WHERE dataset_id = ? AND extension_key = ?",
        [str(dataset.id), extension_key],
    ).fetchone()
    if row is None:
        return None

    dt_id, name, desc, tbl_name, meta_json, o_mode, o_type, o_iqr, o_min_en, o_min, o_max_en, o_max = row
    variables = _load_variables(con, dt_id)
    df = _load_dataframe(con, tbl_name, dt_id)
    metadata = _loads(meta_json)

    dt = Datatable(dataset=dataset, name=name, description=desc, variables=variables, df=df, metadata=metadata)
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
    return dt


def _load_extension_dataframes(
    con: duckdb.DuckDBPyConnection,
    dataset_id: str,
    extension_key: str,
) -> dict[str, pd.DataFrame]:
    """Load raw_data dict[str, DataFrame] for an IntelliCage/IntelliMaze extension."""
    rows = con.execute(
        "SELECT data_key, duckdb_table_name FROM _meta_extension_dataframes WHERE dataset_id = ? AND extension_key = ?",
        [dataset_id, extension_key],
    ).fetchall()
    raw_data: dict[str, pd.DataFrame] = {}
    for data_key, tbl_name in rows:
        owner_id = f"ext_{dataset_id[:12]}_{extension_key}_{data_key}"
        raw_data[data_key] = _load_dataframe(con, tbl_name, owner_id)
    return raw_data


def _load_extensions_phenomaster(con: duckdb.DuckDBPyConnection, dataset: Dataset) -> None:
    from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset

    if not isinstance(dataset, PhenoMasterDataset):
        return

    rows = con.execute(
        "SELECT extension_key, extension_class, extension_name, extra_json FROM _meta_extensions WHERE dataset_id = ?",
        [str(dataset.id)],
    ).fetchall()

    for key, ext_class_fqn, ext_name, extra_json in rows:
        ext_cls = _import_class(ext_class_fqn)
        raw_dt = _load_extension_datatable(con, dataset, key)
        if raw_dt is None:
            continue

        ext_obj = ext_cls.__new__(ext_cls)
        ext_obj.dataset = dataset
        ext_obj.name = ext_name
        ext_obj.raw_datatable = raw_dt

        extra = _loads(extra_json)
        if "ref_box_mapping" in extra:
            ext_obj.ref_box_mapping = {int(k): v for k, v in extra["ref_box_mapping"].items()}
        if "animal_ids" in extra:
            ext_obj.animal_ids = extra["animal_ids"]

        dataset.extensions_data[key] = ext_obj


def _load_extensions_intellicage(con: duckdb.DuckDBPyConnection, dataset: Dataset) -> None:
    from tse_analytics.modules.intellicage.data.intellicage_data import IntelliCageData
    from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset

    if not isinstance(dataset, IntelliCageDataset):
        return

    row = con.execute(
        "SELECT extension_key, extension_name, extra_json "
        "FROM _meta_extensions WHERE dataset_id = ? AND extension_key = 'intellicage_data'",
        [str(dataset.id)],
    ).fetchone()
    if row is None:
        return

    _, ext_name, extra_json = row
    extra = _loads(extra_json)

    raw_data = _load_extension_dataframes(con, str(dataset.id), "intellicage_data")

    ic = IntelliCageData.__new__(IntelliCageData)
    ic.dataset = dataset
    ic.name = ext_name
    ic.raw_data = raw_data
    ic.device_ids = extra.get("device_ids", [])

    dataset.intellicage_data = ic


def _load_extensions_intellimaze(con: duckdb.DuckDBPyConnection, dataset: Dataset) -> None:
    from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset

    if not isinstance(dataset, IntelliMazeDataset):
        return

    rows = con.execute(
        "SELECT extension_key, extension_class, extension_name, extra_json FROM _meta_extensions WHERE dataset_id = ?",
        [str(dataset.id)],
    ).fetchall()

    for key, ext_class_fqn, ext_name, extra_json in rows:
        ext_cls = _import_class(ext_class_fqn)
        extra = _loads(extra_json)
        raw_data = _load_extension_dataframes(con, str(dataset.id), key)

        ext_obj = ext_cls.__new__(ext_cls)
        ext_obj.dataset = dataset
        ext_obj.name = ext_name
        ext_obj.raw_data = raw_data
        ext_obj.device_ids = extra.get("device_ids", [])

        dataset.extensions_data[key] = ext_obj


def _load_dataset(con: duckdb.DuckDBPyConnection, ds_id: str, ds_class_fqn: str, meta_json: str) -> Dataset:
    data = _loads(meta_json)
    metadata = data["metadata"]
    extra_init = data.get("extra_init", {})

    animals = _load_animals(con, ds_id)

    ds_cls = _import_class(ds_class_fqn)

    # IntelliMazeDataset needs extra 'devices' param
    from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset

    if issubclass(ds_cls, IntelliMazeDataset):
        dataset = ds_cls(metadata=metadata, animals=animals, devices=extra_init.get("devices", {}))
    else:
        dataset = ds_cls(metadata=metadata, animals=animals)

    dataset.id = UUID(ds_id)
    dataset.factors = _load_factors(con, ds_id)
    dataset.binning_settings = _load_binning_settings(con, ds_id)
    dataset.reports = _load_reports(con, ds_id, dataset)
    dataset.datatables = _load_datatables_for_dataset(con, dataset)

    _load_extensions_phenomaster(con, dataset)
    _load_extensions_intellicage(con, dataset)
    _load_extensions_intellimaze(con, dataset)

    return dataset


def load_workspace(path: str) -> Workspace:
    """Load a Workspace from a DuckDB file.

    Args:
        path: Path to the DuckDB file.

    Returns:
        The reconstructed Workspace.
    """
    logger.info("Loading workspace from {}", path)
    con = duckdb.connect(str(path), read_only=True)
    try:
        workspace = _load_workspace_meta(con)

        ds_rows = con.execute("SELECT id, dataset_class, metadata_json FROM _meta_datasets").fetchall()
        for ds_id, ds_class_fqn, meta_json in ds_rows:
            dataset = _load_dataset(con, ds_id, ds_class_fqn, meta_json)
            workspace.datasets[dataset.id] = dataset
    finally:
        con.close()

    logger.info("Workspace loaded successfully")
    return workspace
