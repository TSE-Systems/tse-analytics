"""
Module containing the Datatable class for managing tabular data in experiments.

This module provides functionality for handling tabular data, including filtering,
preprocessing, and analysis operations. It supports operations like renaming animals,
excluding time ranges, resampling, and applying factors.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

import pandas as pd

from tse_analytics.core.data.helper import rename_animal_df, reassign_df_timedelta_and_bin
from tse_analytics.core.data.outliers import OutliersMode
from tse_analytics.core.data.pipeline.animal_filter_pipe_operator import filter_animals
from tse_analytics.core.data.pipeline.group_by_pipe_operator import group_by_columns
from tse_analytics.core.data.pipeline.outliers_pipe_operator import process_outliers
from tse_analytics.core.data.pipeline.time_binning_pipe_operator import process_time_binning
from tse_analytics.core.data.shared import Animal, Factor, SplitMode, Variable


class Datatable:
    """
    A class representing a data table in an experiment.

    The Datatable class manages tabular data, including variables and a pandas DataFrame.
    It provides methods for manipulating the data, such as filtering animals, excluding
    time ranges, resampling, and applying factors. It also has methods for retrieving
    processed data frames for analysis.
    """

    """Default columns that are always present in a datatable."""
    default_columns = ["Animal", "Timedelta", "DateTime"]

    def __init__(
        self,
        dataset: "Dataset",
        name: str,
        description: str,
        variables: dict[str, Variable],
        df: pd.DataFrame,
        sampling_interval: pd.Timedelta | None,
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
        sampling_interval : pd.Timedelta or None
            The sampling interval of the data, or None if not applicable.
        """
        self.id = uuid4()
        self.dataset = dataset
        self.name = name
        self.description = description
        self.variables = variables

        self.original_df = df
        self.active_df = self.original_df.copy()

        self.sampling_interval = sampling_interval

    @property
    def start_timestamp(self) -> pd.Timestamp:
        """
        Get the start timestamp of the datatable.

        Returns
        -------
        pd.Timestamp
            The timestamp of the first row in the datatable.
        """
        first_value = self.original_df.at[0, "DateTime"]
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
        last_value = self.original_df.at[self.original_df.index[-1], "DateTime"]
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
        columns = Datatable.default_columns
        if "Bin" in self.original_df.columns:
            columns = columns + ["Bin"]
        if "Run" in self.original_df.columns:
            columns = columns + ["Run"]
        return columns

    def get_categorical_columns(self) -> list[str]:
        """
        Get the categorical columns in the active dataframe.

        Returns
        -------
        list[str]
            List of column names with categorical data type.
        """
        columns = self.active_df.select_dtypes(include=["category"]).columns.tolist()
        return columns

    def get_group_by_columns(self, check_binning=True) -> list[str]:
        """
        Get the columns that can be used for grouping data.

        Parameters
        ----------
        check_binning : bool, default=True
            Whether to check if binning is applied or available.

        Returns
        -------
        list[str]
            List of column names that can be used for grouping data.
        """
        modes = ["Animal"]
        if check_binning:
            if not ("Bin" in self.active_df.columns or self.dataset.binning_settings.apply):
                return modes
        modes.append("Total")
        if self.get_merging_mode() is not None:
            modes.append("Run")
        if len(self.dataset.factors) > 0:
            for factor in self.dataset.factors.keys():
                modes.append(factor)
        return modes

    def delete_variables(self, variable_names: list[str]) -> None:
        """
        Delete variables from the datatable.

        Parameters
        ----------
        variable_names : list[str]
            List of variable names to delete.
        """
        for var_name in variable_names:
            self.variables.pop(var_name)

        self.original_df.drop(columns=variable_names, inplace=True)
        self.active_df.drop(columns=variable_names, inplace=True)

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
        self.original_df = rename_animal_df(self.original_df, old_id, animal)
        self.refresh_active_df()

    def exclude_animals(self, animal_ids: set[str]) -> None:
        """
        Exclude animals from the datatable.

        Parameters
        ----------
        animal_ids : set[str]
            Set of animal IDs to exclude from the datatable.
        """
        self.original_df = self.original_df[~self.original_df["Animal"].isin(animal_ids)]
        self.original_df["Animal"] = self.original_df["Animal"].cat.remove_unused_categories()
        self.original_df.reset_index(inplace=True, drop=True)
        self.refresh_active_df()

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
        self.original_df = self.original_df[
            (self.original_df["DateTime"] < range_start) | (self.original_df["DateTime"] > range_end)
        ]
        merging_mode = self.get_merging_mode()
        self.original_df = reassign_df_timedelta_and_bin(self.original_df, self.sampling_interval, merging_mode)
        self.refresh_active_df()

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
        self.original_df = self.original_df[
            (self.original_df["DateTime"] >= range_start) & (self.original_df["DateTime"] <= range_end)
        ]
        merging_mode = self.get_merging_mode()
        self.original_df = reassign_df_timedelta_and_bin(self.original_df, self.sampling_interval, merging_mode)
        self.refresh_active_df()

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

        if "Run" in self.original_df.columns:
            agg["Run"] = "first"

        for column in self.original_df.columns:
            if column not in self.get_default_columns():
                if self.original_df.dtypes[column].name != "category" and column in self.variables:
                    agg[column] = self.variables[column].aggregation

        result = self.original_df.groupby(["Animal"], dropna=False, observed=False)
        result = result.resample(resampling_interval, on="Timedelta", origin=self.dataset.experiment_started).agg(agg)
        result.reset_index(inplace=True, drop=False)

        # Drop empty entries
        result.dropna(subset=["DateTime"], inplace=True)

        # Assign new bins numbers
        result["Bin"] = (result["Timedelta"] / resampling_interval).round().astype(int)

        result.sort_values(by=["Timedelta", "Animal"], inplace=True)
        result.reset_index(inplace=True, drop=True)

        if "Run" in result.columns:
            result = result.astype({
                "Run": int,
            })

        self.sampling_interval = resampling_interval
        self.original_df = result

        self.refresh_active_df()

    def set_factors(self, factors: dict[str, Factor]) -> None:
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
        df = self.original_df.copy()

        animal_ids = df["Animal"].unique()

        for factor in factors.values():
            animal_factor_map: dict[str, Any] = {}
            for animal_id in animal_ids:
                animal_factor_map[animal_id] = pd.NA

            for level in factor.levels:
                for animal_id in level.animal_ids:
                    animal_factor_map[animal_id] = level.name

            df[factor.name] = df["Animal"].astype(str)
            df.replace({factor.name: animal_factor_map}, inplace=True)
            df[factor.name] = df[factor.name].astype("category")

        self.active_df = df

    def get_df(
        self,
        variable_columns: list[str],
        split_mode: SplitMode,
        factor_name: str,
    ) -> pd.DataFrame:
        """
        Get a dataframe with the specified variables and split mode.

        This method returns a dataframe containing the specified variables,
        with appropriate grouping based on the split mode.

        Parameters
        ----------
        variable_columns : list[str]
            List of variable column names to include in the dataframe.
        split_mode : SplitMode
            The mode to use for splitting the data (by animal, factor, run, or total).
        factor_name : str
            The name of the factor to use when split_mode is FACTOR.

        Returns
        -------
        pd.DataFrame
            A dataframe containing the specified variables with appropriate grouping.
        """
        if self.dataset.binning_settings.apply:
            # Binning is applied
            variables = {col: self.variables[col] for col in variable_columns}
            df = self.get_preprocessed_df(
                variables,
                split_mode,
                factor_name,
                False,
            )
        else:
            match split_mode:
                case SplitMode.ANIMAL:
                    columns = variable_columns + ["Animal"]
                case SplitMode.RUN:
                    columns = variable_columns + ["Run"]
                case SplitMode.FACTOR:
                    columns = variable_columns + [factor_name]
                case _:
                    # Split by total
                    columns = variable_columns
            df = self.get_filtered_df(columns)
        return df

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
        df = self.active_df[columns]

        # Filter animals
        df = filter_animals(df, self.dataset.animals).copy()

        # Outliers removal
        if self.dataset.outliers_settings.mode == OutliersMode.REMOVE:
            variables = {k: v for k, v in self.variables.items() if k in columns}
            df = process_outliers(df, self.dataset.outliers_settings, variables)

        return df

    def get_preprocessed_df(
        self,
        variables: dict[str, Variable],
        split_mode=SplitMode.ANIMAL,
        selected_factor_name: str | None = None,
        dropna=False,
    ) -> pd.DataFrame:
        """
        Get a preprocessed dataframe with time binning and grouping applied.

        Parameters
        ----------
        variables : dict[str, Variable]
            Dictionary mapping variable names to Variable objects.
        split_mode : SplitMode, default=SplitMode.ANIMAL
            The mode to use for splitting the data.
        selected_factor_name : str or None, default=None
            The name of the factor to use when split_mode is FACTOR.
        dropna : bool, default=False
            Whether to drop rows with NaN values.

        Returns
        -------
        pd.DataFrame
            A preprocessed dataframe with time binning and grouping applied.
        """
        columns = self.get_default_columns() + list(self.dataset.factors) + list(variables)
        result = self.get_filtered_df(columns)

        # Time binning
        result = process_time_binning(
            result,
            self.dataset.binning_settings,
            variables,
            self.dataset.experiment_started,
        )

        # Group by columns
        result = group_by_columns(
            result,
            variables,
            split_mode,
            selected_factor_name,
        )

        # TODO: should or should not?
        if dropna:
            result.dropna(inplace=True)

        return result

    def get_preprocessed_df_columns(
        self,
        columns: list[str],
        split_mode=SplitMode.ANIMAL,
        selected_factor_name: str | None = None,
    ) -> pd.DataFrame:
        """
        Get a preprocessed dataframe with specific columns.

        Similar to get_preprocessed_df, but allows specifying exact columns to include.

        Parameters
        ----------
        columns : list[str]
            List of column names to include in the dataframe.
        split_mode : SplitMode, default=SplitMode.ANIMAL
            The mode to use for splitting the data.
        selected_factor_name : str or None, default=None
            The name of the factor to use when split_mode is FACTOR.

        Returns
        -------
        pd.DataFrame
            A preprocessed dataframe with the specified columns.
        """
        result = self.get_filtered_df(columns)

        variables = {key: self.variables[key] for key in columns if key in self.variables}

        # Time binning
        result = process_time_binning(
            result,
            self.dataset.binning_settings,
            variables,
            self.dataset.experiment_started,
        )

        # Group by columns
        result = group_by_columns(
            result,
            variables,
            split_mode,
            selected_factor_name,
        )

        return result

    def refresh_active_df(self) -> None:
        """
        Refresh the active dataframe.

        This method updates the active dataframe by applying the current factors.
        """
        self.set_factors(self.dataset.factors)

    def __getstate__(self):
        """
        Prepare the object state for pickling.

        This method is called when pickling a Datatable object. It removes the
        active_df attribute from the state to avoid pickling large dataframes.

        Returns
        -------
        dict
            The state dictionary to pickle.
        """
        state = self.__dict__.copy()
        # Don't pickle active_df
        del state["active_df"]
        return state
