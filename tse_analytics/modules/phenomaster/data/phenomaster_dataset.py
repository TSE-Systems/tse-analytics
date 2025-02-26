from copy import deepcopy
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

import numpy as np
import pandas as pd

from tse_analytics.core import messaging
from tse_analytics.core.data.binning import BinningMode, BinningSettings, TimeIntervalsBinningSettings
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings
from tse_analytics.core.data.pipeline.animal_filter_pipe_operator import filter_animals
from tse_analytics.core.data.pipeline.outliers_pipe_operator import process_outliers
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.shared import Aggregation, Animal, Factor, Group, SplitMode, Variable
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.modules.phenomaster.submodules.actimot.data.actimot_data import ActimotData
from tse_analytics.modules.phenomaster.submodules.actimot.models.actimot_tree_item import ActimotTreeItem
from tse_analytics.modules.phenomaster.submodules.calo.calo_fitting_result import CaloFittingResult
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_data import CaloData
from tse_analytics.modules.phenomaster.submodules.calo.models.calo_data_tree_item import CaloDataTreeItem
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_data import DrinkFeedData
from tse_analytics.modules.phenomaster.submodules.drinkfeed.models.drinkfeed_data_tree_item import DrinkFeedDataTreeItem
from tse_analytics.modules.phenomaster.submodules.trafficage.data.trafficage_data import TraffiCageData
from tse_analytics.modules.phenomaster.submodules.trafficage.models.trafficage_tree_item import TraffiCageTreeItem


class PhenoMasterDataset:
    def __init__(
        self,
        name: str,
        path: str,
        meta: dict | list[dict],
        animals: dict[str, Animal],
        variables: dict[str, Variable],
        df: pd.DataFrame,
        sampling_interval: pd.Timedelta,
    ):
        self.id = uuid4()
        self.name = name
        self.path = path
        self.meta = meta

        self.animals = animals
        self.variables = variables

        self.original_df = df
        self.active_df = self.original_df.copy()
        self.sampling_interval = sampling_interval

        self.factors: dict[str, Factor] = {}

        self.outliers_settings = OutliersSettings(OutliersMode.OFF, 1.5)
        self.binning_settings = BinningSettings()

        self.calo_data: CaloData | None = None
        self.drinkfeed_data: DrinkFeedData | None = None
        self.actimot_data: ActimotData | None = None
        self.trafficage_data: TraffiCageData | None = None

        self.report = ""

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

    def extract_groups_from_field(self, field: Literal["text1", "text2", "text3"] = "text1") -> dict[str, Group]:
        """Extract groups assignment from Text1, Text2 or Text3 field"""
        groups_dict: dict[str, list[str]] = {}
        for animal in self.animals.values():
            group_name = getattr(animal, field)
            if group_name not in groups_dict:
                groups_dict[group_name] = []
            groups_dict[group_name].append(animal.id)

        groups: dict[str, Group] = {}
        for key, value in groups_dict.items():
            group = Group(key, value)
            groups[group.name] = group
        return groups

    def _rename_animal_df(self, df: pd.DataFrame, old_id: str, animal: Animal) -> pd.DataFrame:
        df = df.astype({
            "Animal": str,
        })
        df.loc[df["Animal"] == old_id, "Animal"] = animal.id
        df = df.astype({
            "Animal": "category",
        })
        return df

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        self.original_df = self._rename_animal_df(self.original_df, old_id, animal)
        self.active_df = self._rename_animal_df(self.active_df, old_id, animal)

        if self.drinkfeed_data is not None:
            self.drinkfeed_data.raw_df = self._rename_animal_df(self.drinkfeed_data.raw_df, old_id, animal)
        if self.calo_data is not None:
            self.calo_data.raw_df = self._rename_animal_df(self.calo_data.raw_df, old_id, animal)
        if self.actimot_data is not None:
            self.actimot_data.raw_df = self._rename_animal_df(self.actimot_data.raw_df, old_id, animal)

        # Rename animal in factor's groups definitions
        for factor in self.factors.values():
            for group in factor.groups:
                for i, animal_id in enumerate(group.animal_ids):
                    if animal_id == old_id:
                        group.animal_ids[i] = animal.id

        # Rename animal in metadata
        new_dict = {}
        for item in self.meta["animals"].values():
            if item["id"] == old_id:
                item["id"] = animal.id
            new_dict[item["id"]] = item
        self.meta["animals"] = new_dict

        # Rename animal in dictionary
        self.animals.pop(old_id)
        self.animals[animal.id] = animal

        messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def exclude_animals(self, animal_ids: set[str]) -> None:
        # Remove animals from factor's groups definitions
        for factor in self.factors.values():
            for group in factor.groups:
                group_set = set(group.animal_ids)
                filtered_set = group_set.difference(animal_ids)
                group.animal_ids = list(filtered_set)

        for animal_id in animal_ids:
            self.animals.pop(animal_id)

        if "animals" in self.meta:
            new_meta_animals = {}
            for item in self.meta["animals"].values():
                if item["id"] not in animal_ids:
                    new_meta_animals[item["id"]] = item
            self.meta["animals"] = new_meta_animals

        self.original_df = self.original_df[~self.original_df["Animal"].isin(animal_ids)]
        self.original_df["Animal"] = self.original_df["Animal"].cat.remove_unused_categories()
        self.original_df.reset_index(inplace=True, drop=True)

        self.refresh_active_df()

        if self.calo_data is not None:
            self.calo_data.raw_df = self.calo_data.raw_df[~self.calo_data.raw_df["Animal"].isin(animal_ids)]
        if self.drinkfeed_data is not None:
            self.drinkfeed_data.raw_df = self.drinkfeed_data.raw_df[
                ~self.drinkfeed_data.raw_df["Animal"].isin(animal_ids)
            ]
        if self.actimot_data is not None:
            self.actimot_data.raw_df = self.actimot_data.raw_df[~self.actimot_data.raw_df["Animal"].isin(animal_ids)]

    def exclude_time(self, range_start: datetime, range_end: datetime) -> None:
        self.original_df = self._exclude_df_time(self.original_df, range_start, range_end)
        self.active_df = self._exclude_df_time(self.active_df, range_start, range_end)

    def _exclude_df_time(self, df: pd.DataFrame, range_start: datetime, range_end: datetime) -> pd.DataFrame:
        df = df[(df["DateTime"] < range_start) | (df["DateTime"] > range_end)]
        df = self._reassign_df_timedelta_and_bin(df, self.sampling_interval)
        return df

    def trim_time(self, range_start: datetime, range_end: datetime) -> None:
        self.original_df = self._trim_df_time(self.original_df, range_start, range_end)
        self.active_df = self._trim_df_time(self.active_df, range_start, range_end)

    def _trim_df_time(self, df: pd.DataFrame, range_start: datetime, range_end: datetime) -> pd.DataFrame:
        df = df[(df["DateTime"] >= range_start) & (df["DateTime"] <= range_end)]
        df = self._reassign_df_timedelta_and_bin(df, self.sampling_interval)
        return df

    def _reassign_df_timedelta_and_bin(self, df: pd.DataFrame, sampling_interval: pd.Timedelta) -> pd.DataFrame:
        df.reset_index(inplace=True, drop=True)

        # Get unique runs numbers
        runs = df["Run"].unique().tolist()

        # Reassign timedeltas
        for run in runs:
            # Get start timestamp per run
            start_date_time = df[df["Run"] == run]["DateTime"].iloc[0]
            df.loc[df["Run"] == run, "Timedelta"] = df["DateTime"] - start_date_time

        # Reassign bins numbers
        df["Bin"] = (df["Timedelta"] / sampling_interval).round().astype(int)
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

        original_result = self._reassign_df_timedelta_and_bin(original_result, resampling_interval)

        self.sampling_interval = resampling_interval
        self.original_df = original_result

        self.refresh_active_df()

    def adjust_time(self, delta: pd.Timedelta) -> None:
        self.original_df = self._adjust_df_time(self.original_df, delta)
        self.active_df = self._adjust_df_time(self.active_df, delta)

    def _adjust_df_time(self, df: pd.DataFrame, delta: pd.Timedelta) -> pd.DataFrame:
        df["DateTime"] = df["DateTime"] + delta
        df = self._reassign_df_timedelta_and_bin(df, self.sampling_interval)
        return df

    def set_factors(self, factors: dict[str, Factor]) -> None:
        self.factors = factors

        # TODO: should be copy?
        df = self.original_df.copy()

        animal_ids = df["Animal"].unique()

        for factor in self.factors.values():
            animal_factor_map: dict[str, Any] = {}
            for animal_id in animal_ids:
                animal_factor_map[animal_id] = pd.NA

            for group in factor.groups:
                for animal_id in group.animal_ids:
                    animal_factor_map[animal_id] = group.name

            df[factor.name] = df["Animal"].astype(str)
            # df[factor.name].replace(animal_factor_map, inplace=True)
            # df[factor.name] = df[factor.name].replace(animal_factor_map)
            df.replace({factor.name: animal_factor_map}, inplace=True)
            df[factor.name] = df[factor.name].astype("category")

        self.active_df = df

    def refresh_active_df(self) -> None:
        self.set_factors(self.factors)

    def _preprocess_df(
        self,
        df: pd.DataFrame,
        variables: [str, Variable],
    ) -> pd.DataFrame:
        # Filter animals
        df = filter_animals(df, self.animals)

        # Outliers removal
        if self.outliers_settings.mode == OutliersMode.REMOVE:
            df = process_outliers(df, self.outliers_settings, variables)

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
            factor_columns = list(self.factors)
            variable_columns = list(variables)
            result = self.active_df[default_columns + factor_columns + variable_columns].copy()
        else:
            variables = self.variables
            result = self.active_df.copy()

        result = self._preprocess_df(result, variables)

        # Binning
        if self.binning_settings.apply:
            match self.binning_settings.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        self.binning_settings.time_intervals_settings,
                        variables,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        self.binning_settings.time_cycles_settings,
                        variables,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        self.binning_settings.time_phases_settings,
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
        factor_columns = list(self.factors)
        variable_columns = list(variables)
        result = self.active_df[default_columns + factor_columns + variable_columns].copy()

        result = self._preprocess_df(result, variables)

        # Binning
        if self.binning_settings.apply:
            match self.binning_settings.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        self.binning_settings.time_intervals_settings,
                        variables,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        self.binning_settings.time_cycles_settings,
                        variables,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        self.binning_settings.time_phases_settings,
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
        factor_columns = list(self.factors)
        result = self.active_df[default_columns + factor_columns + [variable.name]].copy()

        variables = {variable.name: variable}

        result = self._preprocess_df(result, variables)

        # Binning
        if self.binning_settings.apply:
            # if split_mode == SplitMode.ANIMAL:
            #     calculate_errors = None
            result = process_time_interval_binning(
                result,
                self.binning_settings.time_intervals_settings,
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
        factor_columns = list(self.factors)
        result = self.active_df[default_columns + factor_columns].copy()

        variables = {variable.name: variable}

        result = self._preprocess_df(result, variables)

        match self.binning_settings.mode:
            case BinningMode.CYCLES:
                result = process_time_cycles_binning(
                    result,
                    self.binning_settings.time_cycles_settings,
                    variables,
                )
            case BinningMode.PHASES:
                result = process_time_phases_binning(
                    result,
                    self.binning_settings.time_phases_settings,
                    variables,
                )

        return result

    def get_anova_df(
        self,
        variables: dict[str, Variable],
    ) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
        factor_columns = list(self.factors)
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
        if self.binning_settings.apply:
            result = process_time_interval_binning(
                result,
                self.binning_settings.time_intervals_settings,
                variables,
            )

        return result

    def append_fitting_results(
        self,
        fitting_results: dict[int, CaloFittingResult],
    ) -> None:
        if len(fitting_results) > 0:
            active_df = self.original_df
            active_df["O2-p"] = np.nan
            active_df["CO2-p"] = np.nan
            active_df["VO2(3)-p"] = np.nan
            active_df["VCO2(3)-p"] = np.nan
            active_df["RER-p"] = np.nan
            active_df["H(3)-p"] = np.nan
            for result in fitting_results.values():
                for _index, row in result.df.iterrows():
                    bin_number = row["Bin"]

                    # TODO: TODO: check int -> str conversion for general table!
                    active_df.loc[
                        active_df[(active_df["Box"] == result.box_number) & (active_df["Bin"] == bin_number)].index[0],
                        ["O2-p", "CO2-p", "VO2(3)-p", "VCO2(3)-p", "RER-p", "H(3)-p"],
                    ] = [row["O2-p"], row["CO2-p"], row["VO2(3)-p"], row["VCO2(3)-p"], row["RER-p"], row["H(3)-p"]]

            if "O2-p" not in self.variables:
                self.variables["O2-p"] = Variable("O2-p", "[%]", "Predicted O2", "float64", Aggregation.MEAN, False)
            if "CO2-p" not in self.variables:
                self.variables["CO2-p"] = Variable("CO2-p", "[%]", "Predicted CO2", "float64", Aggregation.MEAN, False)
            if "VO2(3)-p" not in self.variables:
                self.variables["VO2(3)-p"] = Variable(
                    "VO2(3)-p", "[ml/h]", "Predicted VO2(3)", "float64", Aggregation.MEAN, False
                )
            if "VCO2(3)-p" not in self.variables:
                self.variables["VCO2(3)-p"] = Variable(
                    "VCO2(3)-p", "[ml/h]", "Predicted VCO2(3)", "float64", Aggregation.MEAN, False
                )
            if "RER-p" not in self.variables:
                self.variables["RER-p"] = Variable("RER-p", "", "Predicted RER", "float64", Aggregation.MEAN, False)
            if "H(3)-p" not in self.variables:
                self.variables["H(3)-p"] = Variable(
                    "H(3)-p", "[kcal/h]", "Predicted H(3)", "float64", Aggregation.MEAN, False
                )
            self.refresh_active_df()
            messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def export_to_excel(self, path: str) -> None:
        with pd.ExcelWriter(path) as writer:
            self.get_current_df().to_excel(writer, sheet_name="Data")

    def export_to_csv(self, path: str) -> None:
        self.get_current_df().to_csv(path, sep=";", index=False)

    def apply_binning(self, binning_settings: BinningSettings) -> None:
        self.binning_settings = binning_settings
        messaging.broadcast(messaging.BinningMessage(self, self, binning_settings))

    def apply_outliers(self, settings: OutliersSettings) -> None:
        self.outliers_settings = settings
        messaging.broadcast(messaging.DataChangedMessage(self, self))

    def clone(self):
        return deepcopy(self)

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        if self.drinkfeed_data is not None:
            dataset_tree_item.add_child(DrinkFeedDataTreeItem(self.drinkfeed_data))

        if self.actimot_data is not None:
            dataset_tree_item.add_child(ActimotTreeItem(self.actimot_data))

        if self.calo_data is not None:
            dataset_tree_item.add_child(CaloDataTreeItem(self.calo_data))

        if self.trafficage_data is not None:
            dataset_tree_item.add_child(TraffiCageTreeItem(self.trafficage_data))

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["active_df"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.refresh_active_df()
