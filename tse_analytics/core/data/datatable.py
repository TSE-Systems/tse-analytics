from datetime import datetime
from typing import Any
from uuid import uuid4

import pandas as pd

from tse_analytics.core.data.binning import BinningMode, TimeIntervalsBinningSettings
from tse_analytics.core.data.helper import rename_animal_df, reassign_df_timedelta_and_bin
from tse_analytics.core.data.outliers import OutliersMode
from tse_analytics.core.data.pipeline.animal_filter_pipe_operator import filter_animals
from tse_analytics.core.data.pipeline.outliers_pipe_operator import process_outliers
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.shared import Animal, Factor, SplitMode, Variable


class Datatable:
    def __init__(
        self,
        dataset: 'Dataset',
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

    def delete_variables(self, variable_names: list[str]) -> None:
        for var_name in variable_names:
            self.variables.pop(var_name)

        self.original_df.drop(columns=variable_names, inplace=True)
        self.active_df.drop(columns=variable_names, inplace=True)

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        self.original_df = rename_animal_df(self.original_df, old_id, animal)
        self.active_df = rename_animal_df(self.active_df, old_id, animal)

    def exclude_animals(self, animal_ids: set[str]) -> None:
        self.original_df = self.original_df[~self.original_df["Animal"].isin(animal_ids)]
        self.original_df["Animal"] = self.original_df["Animal"].cat.remove_unused_categories()
        self.original_df.reset_index(inplace=True, drop=True)
        self.refresh_active_df()

    def exclude_time(self, range_start: datetime, range_end: datetime) -> None:
        self.original_df = self._exclude_df_time(self.original_df, range_start, range_end)
        self.active_df = self._exclude_df_time(self.active_df, range_start, range_end)

    def _exclude_df_time(self, df: pd.DataFrame, range_start: datetime, range_end: datetime) -> pd.DataFrame:
        df = df[(df["DateTime"] < range_start) | (df["DateTime"] > range_end)]
        df = reassign_df_timedelta_and_bin(df, self.sampling_interval)
        return df

    def trim_time(self, range_start: datetime, range_end: datetime) -> None:
        self.original_df = self._trim_df_time(self.original_df, range_start, range_end)
        self.active_df = self._trim_df_time(self.active_df, range_start, range_end)

    def _trim_df_time(self, df: pd.DataFrame, range_start: datetime, range_end: datetime) -> pd.DataFrame:
        df = df[(df["DateTime"] >= range_start) & (df["DateTime"] <= range_end)]
        df = reassign_df_timedelta_and_bin(df, self.sampling_interval)
        return df

    def resample(self, resampling_interval: pd.Timedelta) -> None:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]

        agg = {
            "DateTime": "first",
            "Box": "first",
            "Run": "first",
        }
        for column in self.original_df.columns:
            if column not in default_columns:
                if self.original_df.dtypes[column].name != "category":
                    if column in self.variables:
                        agg[column] = self.variables[column].aggregation
                    else:
                        agg[column] = "mean"

        group_by = ["Animal"]
        sort_by = ["Timedelta", "Box"]

        original_result = self.original_df.groupby(group_by, dropna=False, observed=False)
        original_result = original_result.resample(resampling_interval, on="Timedelta", origin="start").agg(agg)
        original_result.reset_index(inplace=True, drop=False)
        original_result.sort_values(by=sort_by, inplace=True)

        original_result = reassign_df_timedelta_and_bin(original_result, resampling_interval)

        self.sampling_interval = resampling_interval
        self.original_df = original_result

        self.refresh_active_df()

    def adjust_time(self, delta: pd.Timedelta) -> None:
        self.original_df = self._adjust_df_time(self.original_df, delta)
        self.active_df = self._adjust_df_time(self.active_df, delta)

    def _adjust_df_time(self, df: pd.DataFrame, delta: pd.Timedelta) -> pd.DataFrame:
        df["DateTime"] = df["DateTime"] + delta
        df = reassign_df_timedelta_and_bin(df, self.sampling_interval)
        return df

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
            # df[factor.name].replace(animal_factor_map, inplace=True)
            # df[factor.name] = df[factor.name].replace(animal_factor_map)
            df.replace({factor.name: animal_factor_map}, inplace=True)
            df[factor.name] = df[factor.name].astype("category")

        self.active_df = df

    def _preprocess_df(
        self,
        df: pd.DataFrame,
        variables: [str, Variable],
    ) -> pd.DataFrame:
        # Filter animals
        df = filter_animals(df, self.dataset.animals)

        # Outliers removal
        if self.dataset.outliers_settings.mode == OutliersMode.REMOVE:
            df = process_outliers(df, self.dataset.outliers_settings, variables)

        return df

    def _process_splitting(
        self,
        df: pd.DataFrame,
        split_mode: SplitMode,
        variables: dict[str, Variable],
        selected_factor_name: str,
        calculate_errors: str | None = None,
    ) -> pd.DataFrame:
        match split_mode:
            case SplitMode.ANIMAL:
                # No processing!
                return df
            case SplitMode.FACTOR:
                by = ["Bin", selected_factor_name]
            case SplitMode.RUN:
                by = ["Bin", "Run"]
            case _:  # Total split mode
                by = ["Bin"]

        agg = {}

        if "DateTime" in df.columns:
            agg["DateTime"] = "first"

        if "Timedelta" in df.columns:
            agg["Timedelta"] = "first"

        # TODO: use means only when aggregating in split modes!
        for variable in variables.values():
            agg[variable.name] = "mean"

        # Calculate error for timeline plot
        if calculate_errors is not None:
            var_name = list(variables.values())[0].name
            df["Error"] = df[var_name]
            agg["Error"] = calculate_errors

        if len(agg) == 0:
            return df

        result = df.groupby(by, dropna=False, observed=False).aggregate(agg)
        # result.sort_values(by, inplace=True)
        result.reset_index(inplace=True)
        return result

    def get_current_df(
        self,
        variables: dict[str, Variable] | None = None,
        split_mode=SplitMode.ANIMAL,
        selected_factor_name: str | None = None,
        dropna=False,
    ) -> pd.DataFrame:
        if variables is not None:
            default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
            factor_columns = list(self.dataset.factors)
            variable_columns = list(variables)
            result = self.active_df[default_columns + factor_columns + variable_columns].copy()
        else:
            variables = self.variables
            result = self.active_df.copy()

        result = self._preprocess_df(result, variables)

        # Binning
        settings = self.dataset.binning_settings
        if settings.apply:
            match settings.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        settings.time_intervals_settings,
                        variables,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        settings.time_cycles_settings,
                        variables,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        settings.time_phases_settings,
                        variables,
                    )

        # Splitting
        result = self._process_splitting(
            result,
            split_mode,
            variables,
            selected_factor_name,
        )

        # TODO: should or should not?
        if dropna:
            result.dropna(inplace=True)

        return result

    def get_data_table_df(
        self,
        variables: dict[str, Variable],
        split_mode: SplitMode,
        selected_factor_name: str,
    ) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
        factor_columns = list(self.dataset.factors)
        variable_columns = list(variables)
        result = self.active_df[default_columns + factor_columns + variable_columns].copy()

        result = self._preprocess_df(result, variables)

        # Binning
        settings = self.dataset.binning_settings
        if settings.apply:
            match settings.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        settings.time_intervals_settings,
                        variables,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        settings.time_cycles_settings,
                        variables,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        settings.time_phases_settings,
                        variables,
                    )

        # Splitting
        result = self._process_splitting(
            result,
            split_mode,
            variables,
            selected_factor_name,
        )

        return result

    def get_timeline_plot_df(
        self,
        variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
        calculate_errors: str | None,
    ) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
        factor_columns = list(self.dataset.factors)
        result = self.active_df[default_columns + factor_columns + [variable.name]].copy()

        variables = {variable.name: variable}

        result = self._preprocess_df(result, variables)

        # Binning
        settings = self.dataset.binning_settings
        if settings.apply:
            # if split_mode == SplitMode.ANIMAL:
            #     calculate_errors = None
            result = process_time_interval_binning(
                result,
                settings.time_intervals_settings,
                variables,
                calculate_errors,
            )

        # Splitting
        result = self._process_splitting(
            result,
            split_mode,
            variables,
            selected_factor_name,
            calculate_errors,
        )

        return result

    def get_bar_plot_df(
        self,
        variable: Variable,
    ) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin", variable.name]
        factor_columns = list(self.dataset.factors)
        result = self.active_df[default_columns + factor_columns].copy()

        variables = {variable.name: variable}

        result = self._preprocess_df(result, variables)

        settings = self.dataset.binning_settings
        match settings.mode:
            case BinningMode.CYCLES:
                result = process_time_cycles_binning(
                    result,
                    settings.time_cycles_settings,
                    variables,
                )
            case BinningMode.PHASES:
                result = process_time_phases_binning(
                    result,
                    settings.time_phases_settings,
                    variables,
                )

        return result

    def get_anova_df(
        self,
        variables: dict[str, Variable],
    ) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
        factor_columns = list(self.dataset.factors)
        variable_columns = list(variables)
        result = self.active_df[default_columns + factor_columns + variable_columns].copy()

        result = self._preprocess_df(result, variables)

        # Binning
        result = process_time_interval_binning(
            result,
            TimeIntervalsBinningSettings("day", 365),
            variables,
        )

        # TODO: should or should not?
        result.dropna(inplace=True)

        return result

    def get_timeseries_df(
        self,
        animal: Animal,
        variable: Variable,
    ) -> pd.DataFrame:
        columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", variable.name]
        df = self.active_df[columns].copy()
        df = df[df["Animal"] == animal.id]
        df.reset_index(drop=True, inplace=True)

        variables = {variable.name: variable}

        result = self._preprocess_df(df, variables)

        # Binning
        settings = self.dataset.binning_settings
        if settings.apply:
            result = process_time_interval_binning(
                result,
                settings.time_intervals_settings,
                variables,
            )

        return result

    def export_to_excel(self, path: str) -> None:
        with pd.ExcelWriter(path) as writer:
            self.get_current_df().to_excel(writer, sheet_name="Data")

    def export_to_csv(self, path: str) -> None:
        self.get_current_df().to_csv(path, sep=";", index=False)

    def refresh_active_df(self) -> None:
        self.set_factors(self.dataset.factors)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["active_df"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.refresh_active_df()
