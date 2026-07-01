"""
Module containing the Datatable class for managing tabular data in experiments.

This module provides functionality for handling tabular data, including filtering,
preprocessing, and analysis operations. It supports operations like renaming animals,
excluding time ranges, resampling, and applying factors.
"""

from __future__ import annotations

import copy
from collections.abc import Iterable
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid7

import pandas as pd
from loguru import logger

from tse_analytics.core import messaging
from tse_analytics.core.data.factor_appliers import FACTOR_APPLIERS
from tse_analytics.core.data.operators.outliers_pipe_operator import process_outliers
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings
from tse_analytics.core.data.shared import (
    Aggregation,
    Animal,
    Factor,
    FactorRole,
    Variable,
)
from tse_analytics.core.utils.data import exclude_animals_from_df, reassign_df_timedelta, rename_animal_df

if TYPE_CHECKING:
    from tse_analytics.core.data.dataset import Dataset

# Canonical metadata dict keys. Prefer these constants over string literals so the metadata contract
# is discoverable and typo-proof (see docs/dev/14-universal-datatable.md).
META_ORIGIN = "origin"
"""Provenance label of the producing feature (e.g. ``"Chronobiology"``, ``"DrinkFeedIntervals"``)."""

META_ORIGIN_PATH = "origin_path"
"""Source file path a raw datatable was loaded from."""

META_SAMPLE_INTERVAL = "sample_interval"
"""Regular sampling interval (``pd.Timedelta``); its presence marks a regular time series."""

META_EXTENSION_NAME = "extension_name"
"""Owning extension name; set automatically by ``Dataset.add_raw_datatable``."""


class Datatable:
    """
    A class representing a data table in an experiment.

    The Datatable class manages tabular data, including variables and a pandas DataFrame.
    It provides methods for manipulating the data, such as filtering animals, excluding
    time ranges, resampling, and applying factors. It also has methods for retrieving
    processed data frames for analysis.
    """

    def __init__(
        self,
        dataset: Dataset,
        name: str,
        description: str,
        variables: dict[str, Variable],
        df: pd.DataFrame,
        metadata: dict[str, Any],
    ):
        """
        Initialize a Datatable instance.

        Parameters
        ----------
        dataset : Dataset
            The dataset that this datatable belongs to.
        name : str
            The name of the datatable.
        description : str
            A description of the datatable.
        variables : dict[str, Variable]
            Dictionary mapping variable names to Variable objects.
        df : pd.DataFrame
            The pandas DataFrame containing the data.
        metadata : dict[str, Any]
            Metadata associated with the datatable, such as sampling interval.
        """
        self.id = uuid7()
        self.dataset = dataset
        self.name = name
        self.description = description
        self.variables = variables
        self.df = df
        self.metadata = metadata

        self.outliers_settings = OutliersSettings()

    @classmethod
    def from_dataframe(
        cls,
        dataset: Dataset,
        name: str,
        df: pd.DataFrame,
        *,
        origin: str,
        description: str | None = None,
        id_column: str | None = "Animal",
        variables: dict[str, Variable] | None = None,
        aggregation: Aggregation = Aggregation.MEAN,
        unit: str = "",
        sample_interval: pd.Timedelta | None = None,
        extra_metadata: dict[str, Any] | None = None,
        normalize_dtypes: bool = True,
        apply_factors: bool = True,
    ) -> Datatable:
        """Build a universal :class:`Datatable` from a result DataFrame.

        This is the shared entry point any toolbox widget or extension should use to turn an
        analysis result into a dataset datatable for downstream analysis. It normalizes dtypes,
        casts the identifier column to ``category``, builds :class:`Variable` metadata, records the
        provenance, and (optionally) materializes the dataset factors — replacing the boilerplate
        that used to be duplicated at each generation site. See
        ``docs/dev/14-universal-datatable.md``.

        Parameters
        ----------
        dataset : Dataset
            The dataset the new datatable belongs to.
        name : str
            The datatable name (its key in ``dataset.datatables``).
        df : pd.DataFrame
            The source data. It is copied; the caller's frame is not mutated.
        origin : str
            Provenance label, stored in ``metadata[META_ORIGIN]`` (e.g. ``"Chronobiology"``).
        description : str | None
            Human-readable description; defaults to ``f"{origin} result: {name}"``.
        id_column : str | None
            Identifier column (default ``"Animal"``). If present it is cast to ``category`` and
            excluded from auto-generated variables. Pass ``None`` to disable this handling.
        variables : dict[str, Variable] | None
            When given, used verbatim (full control — auto-generation is skipped). This lets callers
            keep helper columns (e.g. ``Bin``) out of the variable set.
        aggregation : Aggregation
            Default aggregation for auto-generated variables.
        unit : str
            Default unit for auto-generated variables.
        sample_interval : pd.Timedelta | None
            When given, stored in ``metadata[META_SAMPLE_INTERVAL]`` so the table is treated as a
            regular time series.
        extra_metadata : dict[str, Any] | None
            Additional metadata entries merged into the datatable metadata. Values must be
            JSON-native to survive persistence (see the persistence note in the dev docs).
        normalize_dtypes : bool
            When ``True`` (default) run ``df.convert_dtypes()`` to obtain numpy-nullable dtypes
            (the house rule). Set ``False`` to preserve dtypes the caller already controls.
        apply_factors : bool
            When ``True`` (default) call :meth:`set_factors` with the dataset factors — a no-op
            unless the frame has an ``"Animal"`` column.

        Returns
        -------
        Datatable
            The constructed datatable (not yet added to the dataset — call
            ``manager.add_datatable(...)``).
        """
        df = df.copy()
        if normalize_dtypes:
            df = df.convert_dtypes()

        if id_column is not None and id_column in df.columns:
            df[id_column] = df[id_column].astype("category")

        if variables is None:
            variables = {}
            for col in df.columns:
                if col == id_column or not pd.api.types.is_numeric_dtype(df[col]):
                    continue
                variables[col] = Variable(col, unit, col, str(df[col].dtype), aggregation, False)

        metadata: dict[str, Any] = {META_ORIGIN: origin}
        if sample_interval is not None:
            metadata[META_SAMPLE_INTERVAL] = sample_interval
        if extra_metadata:
            metadata.update(extra_metadata)

        datatable = cls(
            dataset,
            name,
            description if description is not None else f"{origin} result: {name}",
            variables,
            df,
            metadata,
        )
        if apply_factors:
            datatable.set_factors(dataset.factors)
        return datatable

    @property
    def extension_name(self) -> str | None:
        return self.metadata.get(META_EXTENSION_NAME, None)

    @property
    def sample_interval(self) -> pd.Timedelta | None:
        # Normalize to a pd.Timedelta: metadata round-trips through a DuckDB JSON column, so a stored
        # Timedelta comes back as a string after a save/load cycle. pd.Timedelta(...) is idempotent.
        value = self.metadata.get(META_SAMPLE_INTERVAL, None)
        return None if value is None else pd.Timedelta(value)

    @property
    def is_regular_timeseries(self) -> bool:
        return self.sample_interval is not None

    @property
    def is_timeseries(self) -> bool:
        """Whether this datatable carries a time axis (a ``DateTime`` column).

        Cross-sectional tables generated by the toolbox (e.g. per-animal chronobiology parameters)
        have no ``DateTime`` column; the time-based members are guarded against that case.
        """
        return "DateTime" in self.df.columns

    @property
    def start_timestamp(self) -> pd.Timestamp:
        """
        Get the start timestamp of the datatable.

        Returns
        -------
        pd.Timestamp
            The timestamp of the first row in the datatable.

        Raises
        ------
        ValueError
            If the datatable has no ``DateTime`` column (not a time series).
        """
        if not self.is_timeseries:
            raise ValueError(f"Datatable {self.name!r} has no DateTime column (not a time series).")
        return self.df["DateTime"].iloc[0]

    @property
    def end_timestamp(self) -> pd.Timestamp:
        """
        Get the end timestamp of the datatable.

        Returns
        -------
        pd.Timestamp
            The timestamp of the last row in the datatable.

        Raises
        ------
        ValueError
            If the datatable has no ``DateTime`` column (not a time series).
        """
        if not self.is_timeseries:
            raise ValueError(f"Datatable {self.name!r} has no DateTime column (not a time series).")
        return self.df["DateTime"].iloc[-1]

    @property
    def duration(self) -> pd.Timedelta:
        """
        Get the duration of the datatable.

        Returns
        -------
        pd.Timedelta
            The time difference between the first and last rows in the datatable.
        """
        return self.end_timestamp - self.start_timestamp

    def get_merging_mode(self) -> str | None:
        """
        Get the merging mode from the dataset metadata.

        Returns
        -------
        str or None
            The merging mode if it exists in the dataset metadata, otherwise None.
        """
        return self.dataset.metadata.get("merging_mode")

    def get_default_columns(self) -> list[str]:
        """
        Get the default columns for this datatable.

        Returns
        -------
        list[str]
            List of default column names.
        """
        columns = ["Animal"]
        if "DateTime" in self.df.columns:
            columns.append("DateTime")
        if "Timedelta" in self.df.columns:
            columns.append("Timedelta")
        return columns

    def get_categorical_columns(self) -> list[str]:
        """
        Get the categorical columns in the active dataframe.

        Returns
        -------
        list[str]
            List of column names with categorical data type.
        """
        columns = self.df.select_dtypes(include=["category"]).columns.tolist()
        return columns

    def get_group_by_columns(
        self,
        show_role: FactorRole | None = None,
    ) -> list[str]:
        """
        Get the columns that can be used for grouping data.

        Returns
        -------
        list[str]
            List of column names that can be used for grouping data.
        """
        if show_role is None:
            return list(self.dataset.factors.keys())
        return [name for name, f in self.dataset.factors.items() if f.role == show_role]

    def apply_outliers(self, settings: OutliersSettings) -> None:
        """
        Apply outlier detection settings to the datatable.

        This method updates the outlier detection settings for the datatable and
        broadcasts a message to notify listeners of the change.

        Parameters
        ----------
        settings : OutliersSettings
            The outlier detection settings to apply to the datatable.
        """
        self.outliers_settings = settings
        messaging.broadcast(messaging.OutliersChangedMessage(self, self))

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        """
        Rename an animal in the datatable.

        Parameters
        ----------
        old_id : str
            The current ID of the animal.
        animal : Animal
            The animal object with the new ID.
        """
        self.df = rename_animal_df(self.df, old_id, animal)

    def exclude_animals(self, animal_ids: set[str]) -> None:
        """
        Exclude animals from the datatable.

        Parameters
        ----------
        animal_ids : set[str]
            Set of animal IDs to exclude from the datatable.
        """
        if "Animal" in self.df.columns:
            self.df = exclude_animals_from_df(self.df, animal_ids)

    def _filter_by_time_mask(self, mask: pd.Series) -> None:
        self.df = self.df[mask]
        self.df = reassign_df_timedelta(self.df, self.get_merging_mode())

    def exclude_time(self, range_start: datetime, range_end: datetime) -> None:
        """
        Exclude a time range from the datatable.

        Parameters
        ----------
        range_start : datetime
            Start of the time range to exclude.
        range_end : datetime
            End of the time range to exclude.

        Notes
        -----
        No-op on cross-sectional datatables (no ``DateTime`` column); this method is driven by
        dataset-wide loops that must skip non-time-series tables.
        """
        if not self.is_timeseries:
            return
        self._filter_by_time_mask((self.df["DateTime"] < range_start) | (self.df["DateTime"] > range_end))

    def trim_time(self, range_start: datetime, range_end: datetime) -> None:
        """
        Trim the datatable to a specific time range.

        Parameters
        ----------
        range_start : datetime
            New start time for the datatable.
        range_end : datetime
            New end time for the datatable.

        Notes
        -----
        No-op on cross-sectional datatables (no ``DateTime`` column); this method is driven by
        dataset-wide loops that must skip non-time-series tables.
        """
        if not self.is_timeseries:
            return
        self._filter_by_time_mask((self.df["DateTime"] >= range_start) & (self.df["DateTime"] <= range_end))

    def resample(self, resample_interval: pd.Timedelta) -> None:
        """
        Resample the datatable to a new time interval.

        This method resamples the data to the specified time interval, aggregating
        variables according to their defined aggregation methods.

        Parameters
        ----------
        resample_interval : pd.Timedelta
            The time interval to resample the data to.

        Notes
        -----
        No-op unless the datatable has the ``Animal``/``DateTime``/``Timedelta`` columns; this method
        is driven by dataset-wide loops that must skip non-time-series tables.
        """
        if not {"Animal", "DateTime", "Timedelta"} <= set(self.df.columns):
            return

        default_cols = set(self.get_default_columns())
        agg: dict[str, Any] = {"DateTime": "first"}
        for column in self.df.columns:
            if column in default_cols:
                continue
            if self.df.dtypes[column].name == "category":
                agg[column] = "first"
            elif column in self.variables:
                agg[column] = self.variables[column].aggregation

        result = self.df.groupby(["Animal"], dropna=False, observed=False)
        result = result.resample(resample_interval, on="Timedelta", origin=self.dataset.experiment_started).agg(agg)

        # Drop empty entries
        result = result[result["DateTime"].notna()].reset_index(drop=False)

        # TODO: check if done properly: align timedelta to the resampling resolution
        result["Timedelta"] = result["Timedelta"].dt.round(resample_interval)

        result.sort_values(by=["Timedelta", "Animal"], inplace=True)
        result.reset_index(inplace=True, drop=True)

        self.metadata[META_SAMPLE_INTERVAL] = resample_interval
        self.df = result

    def set_factors(
        self,
        factors: dict[str, Factor],
        old_factor_names: Iterable[str] | None = None,
    ) -> None:
        """
        Set the factors for the datatable.

        Each factor is materialized as a categorical column on the active
        dataframe by dispatching on the type of ``factor.config``. The
        dispatch table is ``FACTOR_APPLIERS``; adding a new factor source
        requires only a new config type and a new applier function — no
        changes to this method.

        Parameters
        ----------
        factors : dict[str, Factor]
            Dictionary mapping factor names to Factor objects.
        old_factor_names : Iterable[str] | None
            Names of previously applied factors; their columns are dropped
            before re-applying. ``"Animal"`` and ``"Trial"`` are preserved.
        """
        if "Animal" not in self.df.columns:
            return

        # TODO: should be copy?
        df = self.df.copy()

        # Drop old factors but ignore "Animal" and "Trial"
        if old_factor_names is not None:
            cols_to_drop = [n for n in old_factor_names if n not in ("Animal", "Trial")]
            df.drop(columns=cols_to_drop, inplace=True, errors="ignore")

        for factor in factors.values():
            config = factor.config
            if config is None:
                logger.debug(f"Skipping factor {factor.name!r}: no config")
                continue
            applier = FACTOR_APPLIERS.get(type(config))
            if applier is None:
                logger.debug(f"Skipping factor {factor.name!r}: no applier registered for {type(config).__name__}")
                continue
            applier(df, factor, self.dataset)

        self.df = df

    def get_filtered_df(
        self,
        columns: list[str],
    ) -> pd.DataFrame:
        """
        Get a filtered dataframe with the specified columns.

        This method returns a dataframe containing only the specified columns,
        filtered by enabled animals and with outliers removed if configured.

        Parameters
        ----------
        columns : list[str]
            List of column names to include in the dataframe.

        Returns
        -------
        pd.DataFrame
            A filtered dataframe containing the specified columns.
        """
        df = self.df[columns].copy()

        # Outliers removal
        if self.outliers_settings.mode == OutliersMode.REMOVE:
            variables = {k: v for k, v in self.variables.items() if k in columns}
            df = process_outliers(df, self.outliers_settings, variables)

        return df

    def delete_variables(self, variable_names: list[str]) -> None:
        """
        Delete variables from the datatable.

        Parameters
        ----------
        variable_names : list[str]
            List of variable names to delete.
        """
        for var_name in variable_names:
            self.variables.pop(var_name, None)

        self.df.drop(columns=variable_names, inplace=True, errors="ignore")

    def rename_variables(self, variable_name_map: dict[str, str]) -> None:
        for old_name, new_name in variable_name_map.items():
            if old_name in self.variables:
                self.variables[new_name] = self.variables.pop(old_name)
                self.variables[new_name].name = new_name

        # Sort variables by name
        self.variables = dict(sorted(self.variables.items(), key=lambda x: x[0].lower()))

        self.df.rename(columns=variable_name_map, inplace=True, errors="ignore")

    def freeze_outliers_removal(self):
        df = process_outliers(self.df, self.outliers_settings, self.variables)
        self.df = df

    def clone(self):
        # A fresh id is intentional: the persisted DuckDB df-table name is keyed on
        # dataset.id + datatable.id, so a duplicated id would collide (see core/io/storage.py).
        cloned = Datatable(
            self.dataset,
            self.name,
            self.description,
            self.variables.copy(),
            self.df.copy(),
            self.metadata.copy(),
        )
        cloned.outliers_settings = copy.deepcopy(self.outliers_settings)
        return cloned
