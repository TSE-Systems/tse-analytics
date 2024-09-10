from datetime import datetime

import numpy as np
import polars as pl

from tse_analytics.core.data.binning import BinningMode, BinningOperation, BinningParams, TimeIntervalsBinningSettings
from tse_analytics.core.data.outliers import OutliersMode, OutliersParams
from tse_analytics.core.data.pipeline.animal_filter_pipe_operator import filter_animals
from tse_analytics.core.data.pipeline.outliers_pipe_operator import process_outliers
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.shared import Animal, SplitMode, Variable
from tse_analytics.core.messaging.messages import BinningMessage, DataChangedMessage, DatasetChangedMessage
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.modules.phenomaster.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_analytics.modules.phenomaster.calo_details.data.calo_details import CaloDetails
from tse_analytics.modules.phenomaster.data.dataset import Dataset


class DataHub:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger

        self.selected_dataset: Dataset | None = None
        self.selected_animals: list[Animal] = []
        self.selected_variables: list[Variable] = []

        self.binning_params = BinningParams(False, BinningMode.INTERVALS, BinningOperation.MEAN)
        self.outliers_params = OutliersParams(OutliersMode.OFF, 3.0)

    def clear(self):
        self.selected_dataset = None
        self.selected_animals.clear()
        self.selected_variables.clear()

        self.messenger.broadcast(DatasetChangedMessage(self, None))

    def apply_binning(self, params: BinningParams):
        if self.selected_dataset is None:
            return

        self.binning_params = params
        self.messenger.broadcast(BinningMessage(self, self.binning_params))

    def apply_outliers(self, params: OutliersParams):
        if self.selected_dataset is None:
            return
        self.outliers_params = params
        self.messenger.broadcast(DataChangedMessage(self))

    def set_selected_dataset(self, dataset: Dataset) -> None:
        self.selected_dataset = dataset
        self.selected_animals.clear()
        self.selected_variables.clear()

        self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        self.selected_dataset.rename_animal(old_id, animal)
        self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def set_selected_animals(self, animals: list[Animal]) -> None:
        self.selected_animals = animals
        self._broadcast_data_changed()

    def exclude_animals(self) -> None:
        animal_ids = [animal.id for animal in self.selected_animals]
        self.selected_dataset.exclude_animals(animal_ids)
        self.selected_animals = []
        self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def exclude_time(self, start: datetime, end: datetime) -> None:
        self.selected_dataset.exclude_time(start, end)
        self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def set_selected_variables(self, variables: list[Variable]) -> None:
        self.selected_variables = variables
        self._broadcast_data_changed()

    def _broadcast_data_changed(self):
        self.messenger.broadcast(DataChangedMessage(self))

    def adjust_dataset_time(self, delta: str) -> None:
        if self.selected_dataset is not None:
            self.selected_dataset.adjust_time(pl.Duration(delta))
            self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def export_to_excel(self, path: str) -> None:
        if self.selected_dataset is not None:
            self.get_current_df().write_excel(path, worksheet="Data")

    def export_to_csv(self, path: str) -> None:
        if self.selected_dataset is not None:
            self.get_current_df().write_csv(path, separator=";")

    def append_fitting_results(
        self, calo_details: CaloDetails, fitting_results: dict[int, CaloDetailsFittingResult]
    ) -> None:
        if calo_details is not None and len(fitting_results) > 0:
            dataset = calo_details.dataset
            active_df = dataset.original_df
            active_df["O2-p"] = np.NaN
            active_df["CO2-p"] = np.NaN
            active_df["VO2(3)-p"] = np.NaN
            active_df["VCO2(3)-p"] = np.NaN
            active_df["RER-p"] = np.NaN
            active_df["H(3)-p"] = np.NaN
            for result in fitting_results.values():
                for _index, row in result.df.iterrows():
                    bin_number = row["Bin"]

                    # TODO: TODO: check int -> str conversion for general table!
                    active_df.loc[
                        active_df[(active_df["Box"] == result.box_number) & (active_df["Bin"] == bin_number)].index[0],
                        ["O2-p", "CO2-p", "VO2(3)-p", "VCO2(3)-p", "RER-p", "H(3)-p"],
                    ] = [row["O2-p"], row["CO2-p"], row["VO2(3)-p"], row["VCO2(3)-p"], row["RER-p"], row["H(3)-p"]]

            if "O2-p" not in dataset.variables:
                dataset.variables["O2-p"] = Variable("O2-p", "[%]", "Predicted O2", type="float64")
            if "CO2-p" not in dataset.variables:
                dataset.variables["CO2-p"] = Variable("CO2-p", "[%]", "Predicted CO2", type="float64")
            if "VO2(3)-p" not in dataset.variables:
                dataset.variables["VO2(3)-p"] = Variable("VO2(3)-p", "[ml/h]", "Predicted VO2(3)", type="float64")
            if "VCO2(3)-p" not in dataset.variables:
                dataset.variables["VCO2(3)-p"] = Variable("VCO2(3)-p", "[ml/h]", "Predicted VCO2(3)", type="float64")
            if "RER-p" not in dataset.variables:
                dataset.variables["RER-p"] = Variable("RER-p", "", "Predicted RER", type="float64")
            if "H(3)-p" not in dataset.variables:
                dataset.variables["H(3)-p"] = Variable("H(3)-p", "[kcal/h]", "Predicted H(3)", type="float64")
            dataset.refresh_active_df()
            self.set_selected_dataset(dataset)

    def get_current_df(
        self,
        variables: list[str] | None = None,
        split_mode=SplitMode.ANIMAL,
        selected_factor: str | None = None,
        dropna=False,
    ) -> pl.DataFrame:
        if variables is not None:
            default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
            factor_columns = list(self.selected_dataset.factors.keys())
            result = self.selected_dataset.active_df[default_columns + factor_columns + variables].copy()
        else:
            result = self.selected_dataset.active_df.copy()

        # Filter operator
        animals = [animal for animal in self.selected_dataset.animals.values() if animal.enabled]
        result = filter_animals(result, animals)

        # Outliers operator
        if self.outliers_params.mode == OutliersMode.REMOVE:
            if variables is None:
                variables = list(self.selected_dataset.variables.keys())
            result = process_outliers(result, self.outliers_params, variables)

        # Binning
        if self.binning_params.apply:
            factor_names = list(self.selected_dataset.factors.keys())
            match self.binning_params.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        self.selected_dataset.binning_settings.time_intervals_settings,
                        self.binning_params.operation,
                        split_mode,
                        factor_names,
                        selected_factor,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        self.selected_dataset.binning_settings.time_cycles_settings,
                        self.binning_params.operation,
                        split_mode,
                        factor_names,
                        selected_factor,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        self.selected_dataset.binning_settings.time_phases_settings,
                        self.binning_params.operation,
                        split_mode,
                        factor_names,
                        selected_factor,
                    )

        # TODO: should or should not?
        if dropna:
            result = result.dropna()

        return result

    def get_data_view_df(
        self,
        variables: list[str] | None = None,
        split_mode=SplitMode.ANIMAL,
        selected_factor: str | None = None,
        dropna=False,
    ) -> pl.DataFrame:
        factor_columns = list(self.selected_dataset.factors.keys())
        columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"] + factor_columns
        if len(variables) > 0:
            columns = columns + variables
        result = self.selected_dataset.active_df.select(columns)

        # Filter operator
        if len(self.selected_animals) > 0:
            result = filter_animals(result, self.selected_animals)

        # Outliers operator
        if self.outliers_params.mode == OutliersMode.REMOVE:
            if variables is None:
                variables = list(self.selected_dataset.variables.keys())
            result = process_outliers(result, self.outliers_params, variables)

        # Binning
        if self.binning_params.apply:
            factor_names = list(self.selected_dataset.factors.keys())
            match self.binning_params.mode:
                case BinningMode.INTERVALS:
                    result = process_time_interval_binning(
                        result,
                        self.selected_dataset.binning_settings.time_intervals_settings,
                        self.binning_params.operation,
                        split_mode,
                        factor_names,
                        selected_factor,
                    )
                case BinningMode.CYCLES:
                    result = process_time_cycles_binning(
                        result,
                        self.selected_dataset.binning_settings.time_cycles_settings,
                        self.binning_params.operation,
                        split_mode,
                        factor_names,
                        selected_factor,
                    )
                case BinningMode.PHASES:
                    result = process_time_phases_binning(
                        result,
                        self.selected_dataset.binning_settings.time_phases_settings,
                        self.binning_params.operation,
                        split_mode,
                        factor_names,
                        selected_factor,
                    )

        # TODO: should or should not?
        if dropna:
            result = result.dropna()

        return result

    def get_anova_df(self, variables: list[str] | None = None) -> pl.DataFrame:
        if variables is not None:
            default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
            factor_columns = list(self.selected_dataset.factors.keys())
            result = self.selected_dataset.active_df[default_columns + factor_columns + variables].copy()
        else:
            result = self.selected_dataset.active_df.copy()

        # Filter operator
        animals = [animal for animal in self.selected_dataset.animals.values() if animal.enabled]
        result = filter_animals(result, animals)

        # Outliers operator
        if self.outliers_params.mode == OutliersMode.REMOVE:
            if variables is None:
                variables = list(self.selected_dataset.variables.keys())
            result = process_outliers(result, self.outliers_params, variables)

        # Binning
        factor_names = list(self.selected_dataset.factors.keys())
        result = process_time_interval_binning(
            result,
            TimeIntervalsBinningSettings("day", 365),
            BinningOperation.MEAN,
            SplitMode.ANIMAL,
            factor_names,
            None,
        )

        # TODO: should or should not?
        result = result.dropna()

        return result

    def get_bar_plot_df(
        self,
        variable: str,
    ) -> pl.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin", variable]
        factor_columns = list(self.selected_dataset.factors.keys())
        result = self.selected_dataset.active_df[default_columns + factor_columns].copy()

        # Filter operator
        if len(self.selected_animals) > 0:
            result = filter_animals(result, self.selected_animals)

        # Outliers operator
        if self.outliers_params.mode == OutliersMode.REMOVE:
            result = process_outliers(result, self.outliers_params, [variable])

        if self.binning_params.mode == BinningMode.CYCLES:

            def filter_method(x):
                return (
                    "Light"
                    if self.selected_dataset.binning_settings.time_cycles_settings.light_cycle_start
                    <= x.time()
                    < self.selected_dataset.binning_settings.time_cycles_settings.dark_cycle_start
                    else "Dark"
                )

            result["Bin"] = result["DateTime"].apply(filter_method).astype("category")
            result.drop(columns=["DateTime"], inplace=True)
        elif self.binning_params.mode == BinningMode.PHASES:
            self.selected_dataset.binning_settings.time_phases_settings.time_phases.sort(
                key=lambda x: x.start_timestamp
            )

            result["Bin"] = None
            for phase in self.selected_dataset.binning_settings.time_phases_settings.time_phases:
                result.loc[result["Timedelta"] >= phase.start_timestamp, "Bin"] = phase.name

            result["Bin"] = result["Bin"].astype("category")
            result.drop(columns=["DateTime"], inplace=True)

            # Sort category names by time
            categories = [item.name for item in self.selected_dataset.binning_settings.time_phases_settings.time_phases]
            result["Bin"] = result["Bin"].cat.set_categories(categories, ordered=True)

        return result
