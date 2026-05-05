"""
Module containing the Datatable class for managing tabular data in experiments.

This module provides functionality for handling tabular data, including filtering,
preprocessing, and analysis operations. It supports operations like renaming animals,
excluding time ranges, resampling, and applying factors.
"""

from __future__ import annotations

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
    Animal,
    Factor,
    FactorRole,
    Variable,
)
from tse_analytics.core.utils.data import exclude_animals_from_df, reassign_df_timedelta, rename_animal_df

if TYPE_CHECKING:
    from tse_analytics.core.data.dataset import Dataset


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

    @property
    def extension_name(self) -> str | None:
        return self.metadata.get("extension_name", None)

    @property
    def sample_interval(self) -> pd.Timedelta | None:
        return self.metadata.get("sample_interval", None)

    @property
    def is_regular_timeseries(self) -> bool:
        return self.sample_interval is not None

    @property
    def start_timestamp(self) -> pd.Timestamp:
        """
        Get the start timestamp of the datatable.

        Returns
        -------
        pd.Timestamp
            The timestamp of the first row in the datatable.
        """
        return self.df["DateTime"].iloc[0]

    @property
    def end_timestamp(self) -> pd.Timestamp:
        """
        Get the end timestamp of the datatable.

        Returns
        -------
        pd.Timestamp
            The timestamp of the last row in the datatable.
        """
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
        """
        self._filter_by_time_mask(
            (self.df["DateTime"] < range_start) | (self.df["DateTime"] > range_end)
        )

    def trim_time(self, range_start: datetime, range_end: datetime) -> None:
        """
        Trim the datatable to a specific time range.

        Parameters
        ----------
        range_start : datetime
            New start time for the datatable.
        range_end : datetime
            New end time for the datatable.
        """
        self._filter_by_time_mask(
            (self.df["DateTime"] >= range_start) & (self.df["DateTime"] <= range_end)
        )

    def resample(self, resample_interval: pd.Timedelta) -> None:
        """
        Resample the datatable to a new time interval.

        This method resamples the data to the specified time interval, aggregating
        variables according to their defined aggregation methods.

        Parameters
        ----------
        resample_interval : pd.Timedelta
            The time interval to resample the data to.
        """
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

        self.metadata["sample_interval"] = resample_interval
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
            before re-applying. ``"Animal"`` and ``"Run"`` are preserved.
        """
        if "Animal" not in self.df.columns:
            return

        # TODO: should be copy?
        df = self.df.copy()

        # Drop old factors but ignore "Animal" and "Run"
        if old_factor_names is not None:
            cols_to_drop = [n for n in old_factor_names if n not in ("Animal", "Run")]
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
        return Datatable(
            self.dataset,
            self.name,
            self.description,
            self.variables.copy(),
            self.df.copy(),
            self.metadata.copy(),
        )
