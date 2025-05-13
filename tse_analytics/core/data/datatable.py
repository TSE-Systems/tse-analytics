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
        first_value = self.original_df.at[0, "DateTime"]
        return first_value

    @property
    def end_timestamp(self) -> pd.Timestamp:
        last_value = self.original_df.at[self.original_df.index[-1], "DateTime"]
        return last_value

    @property
    def duration(self) -> pd.Timedelta:
        return self.end_timestamp - self.start_timestamp

    def get_merging_mode(self) -> str | None:
        merging_mode = self.dataset.metadata["merging_mode"] if "merging_mode" in self.dataset.metadata else None
        return merging_mode

    def get_default_columns(self) -> list[str]:
        columns = Datatable.default_columns
        if "Bin" in self.original_df.columns:
            columns = columns + ["Bin"]
        if "Run" in self.original_df.columns:
            columns = columns + ["Run"]
        return columns

    def get_categorical_columns(self) -> list[str]:
        columns = self.active_df.select_dtypes(include=["category"]).columns.tolist()
        return columns

    def get_group_by_columns(self) -> list[str]:
        modes = ["Animal"]
        if "Bin" in self.active_df.columns or self.dataset.binning_settings.apply:
            modes.append("Total")
            if self.get_merging_mode() is not None:
                modes.append("Run")
            if len(self.dataset.factors) > 0:
                for factor in self.dataset.factors.keys():
                    modes.append(factor)
        return modes

    def delete_variables(self, variable_names: list[str]) -> None:
        for var_name in variable_names:
            self.variables.pop(var_name)

        self.original_df.drop(columns=variable_names, inplace=True)
        self.active_df.drop(columns=variable_names, inplace=True)

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        self.original_df = rename_animal_df(self.original_df, old_id, animal)
        self.refresh_active_df()

    def exclude_animals(self, animal_ids: set[str]) -> None:
        self.original_df = self.original_df[~self.original_df["Animal"].isin(animal_ids)]
        self.original_df["Animal"] = self.original_df["Animal"].cat.remove_unused_categories()
        self.original_df.reset_index(inplace=True, drop=True)
        self.refresh_active_df()

    def exclude_time(self, range_start: datetime, range_end: datetime) -> None:
        self.original_df = self.original_df[
            (self.original_df["DateTime"] < range_start) | (self.original_df["DateTime"] > range_end)
        ]
        merging_mode = self.get_merging_mode()
        self.original_df = reassign_df_timedelta_and_bin(self.original_df, self.sampling_interval, merging_mode)
        self.refresh_active_df()

    def trim_time(self, range_start: datetime, range_end: datetime) -> None:
        self.original_df = self.original_df[
            (self.original_df["DateTime"] >= range_start) & (self.original_df["DateTime"] <= range_end)
        ]
        merging_mode = self.get_merging_mode()
        self.original_df = reassign_df_timedelta_and_bin(self.original_df, self.sampling_interval, merging_mode)
        self.refresh_active_df()

    def resample(self, resampling_interval: pd.Timedelta) -> None:
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

    def get_filtered_df(
        self,
        columns: list[str],
    ) -> pd.DataFrame:
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
        dropna=False,
    ) -> pd.DataFrame:
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

        # TODO: should or should not?
        if dropna:
            result.dropna(inplace=True)

        return result

    def refresh_active_df(self) -> None:
        self.set_factors(self.dataset.factors)

    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle active_df
        del state["active_df"]
        return state
