"""
Module containing the Datatable class for managing tabular data in experiments.

This module provides functionality for handling tabular data, including filtering,
preprocessing, and analysis operations. It supports operations like renaming animals,
excluding time ranges, resampling, and applying factors.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid7

import pandas as pd

from tse_analytics.core import messaging
from tse_analytics.core.data.operators.outliers_pipe_operator import process_outliers
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings
from tse_analytics.core.data.shared import Animal, Factor, Variable
from tse_analytics.core.utils.data import exclude_animals_from_df, reassign_df_timedelta_and_bin, rename_animal_df

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

        self.parent_table: Datatable | None = None
        self.derived_tables: dict[str, Datatable] = {}

    @property
    def sampling_interval(self) -> pd.Timedelta | None:
        return self.metadata.get("sampling_interval", None)

    @property
    def is_regular_timeseries(self) -> bool:
        return self.sampling_interval is not None

    @property
    def start_timestamp(self) -> pd.Timestamp:
        """
        Get the start timestamp of the datatable.

        Returns
        -------
        pd.Timestamp
            The timestamp of the first row in the datatable.
        """
        first_value = self.df.at[0, "DateTime"]
        return first_value

    @property
    def end_timestamp(self) -> pd.Timestamp:
        """
        Get the end timestamp of the datatable.

        Returns
        -------
        pd.Timestamp
            The timestamp of the last row in the datatable.
        """
        last_value = self.df.at[self.df.index[-1], "DateTime"]
        return last_value

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
        merging_mode = self.dataset.metadata["merging_mode"] if "merging_mode" in self.dataset.metadata else None
        return merging_mode

    def get_default_columns(self) -> list[str]:
        """
        Get the default columns for this datatable.

        Returns
        -------
        list[str]
            List of default column names, including "Bin" and "Run" if they exist.
        """
        columns = ["Animal"]
        if "DateTime" in self.df.columns:
            columns.append("DateTime")
        if "Timedelta" in self.df.columns:
            columns.append("Timedelta")
        if "Bin" in self.df.columns:
            columns.append("Bin")
        if "Run" in self.df.columns:
            columns.append("Run")
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
        disable_total_mode=False,
        disable_run_mode=False,
        disable_animal_mode=False,
    ) -> list[str]:
        """
        Get the columns that can be used for grouping data.

        Returns
        -------
        list[str]
            List of column names that can be used for grouping data.
        """
        modes = ["Animal"] if not disable_animal_mode else []
        if not disable_total_mode:
            modes.append("Total")
        if not disable_run_mode and "Run" in self.df.columns:
            modes.append("Run")
        if len(self.dataset.factors) > 0:
            for factor in self.dataset.factors.keys():
                modes.append(factor)
        return modes

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
        self.df = exclude_animals_from_df(self.df, animal_ids)

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
        self.df = self.df[(self.df["DateTime"] < range_start) | (self.df["DateTime"] > range_end)]
        merging_mode = self.get_merging_mode()
        self.df = reassign_df_timedelta_and_bin(self.df, self.sampling_interval, merging_mode)

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
        self.df = self.df[(self.df["DateTime"] >= range_start) & (self.df["DateTime"] <= range_end)]
        merging_mode = self.get_merging_mode()
        self.df = reassign_df_timedelta_and_bin(self.df, self.sampling_interval, merging_mode)

    def resample(self, resampling_interval: pd.Timedelta) -> None:
        """
        Resample the datatable to a new time interval.

        This method resamples the data to the specified time interval, aggregating
        variables according to their defined aggregation methods.

        Parameters
        ----------
        resampling_interval : pd.Timedelta
            The time interval to resample the data to.
        """
        agg = {
            "DateTime": "first",
        }

        if "Run" in self.df.columns:
            agg["Run"] = "first"

        for column in self.df.columns:
            if column not in self.get_default_columns():
                if self.df.dtypes[column].name != "category" and column in self.variables:
                    agg[column] = self.variables[column].aggregation

        result = self.df.groupby(["Animal"], dropna=False, observed=False)
        result = result.resample(resampling_interval, on="Timedelta", origin=self.dataset.experiment_started).agg(agg)
        result.reset_index(inplace=True, drop=False)

        # Drop empty entries
        result.dropna(subset=["DateTime"], inplace=True)

        # Assign new bins numbers
        result["Bin"] = (result["Timedelta"] / resampling_interval).round().astype("UInt64")

        result.sort_values(by=["Timedelta", "Animal"], inplace=True)
        result.reset_index(inplace=True, drop=True)

        if "Run" in result.columns:
            result = result.astype({
                "Run": "UInt8",
            })

        self.metadata["sampling_interval"] = resampling_interval
        self.df = result

    def set_factors(self, factors: dict[str, Factor], old_factors: dict[str, Factor] | None = None) -> None:
        """
        Set the factors for the datatable.

        This method updates the active dataframe with factor columns based on the
        provided factors dictionary.

        Parameters
        ----------
        factors : dict[str, Factor]
            Dictionary mapping factor names to Factor objects.
        """
        # TODO: should be copy?
        df = self.df.copy()

        # Drop old factors
        if old_factors is not None:
            df.drop(columns=old_factors.keys(), inplace=True)

        animal_ids = df["Animal"].unique()

        for factor in factors.values():
            animal_factor_map: dict[str, Any] = {}
            for animal_id in animal_ids:
                animal_factor_map[animal_id] = pd.NA

            for level in factor.levels:
                for animal_id in level.animal_ids:
                    animal_factor_map[animal_id] = level.name

            df[factor.name] = df["Animal"].astype("string")
            df.replace({factor.name: animal_factor_map}, inplace=True)
            df[factor.name] = df[factor.name].astype("category")

            # Sort levels alphabetically
            order = sorted(df[factor.name].cat.categories.tolist(), key=str.lower)
            df[factor.name] = df[factor.name].cat.reorder_categories(order)

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
        # TODO: Should use the copy?
        df = self.df[columns]

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
                self.variables[new_name] = self.variables.pop(old_name, None)
                self.variables[new_name].name = new_name

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

    def add_derived_table(self, derived_table: Datatable) -> None:
        derived_table.parent_table = self
        self.derived_tables[derived_table.name] = derived_table
