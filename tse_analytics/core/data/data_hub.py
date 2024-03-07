import gc

import numpy as np
import pandas as pd
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QPixmapCache

from tse_analytics.core.data.binning import BinningMode, BinningOperation, BinningParams, TimeIntervalsBinningSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.outliers import OutliersMode, OutliersParams
from tse_analytics.core.data.pipeline.animal_filter_pipe_operator import AnimalFilterPipeOperator
from tse_analytics.core.data.pipeline.outliers_pipe_operator import OutliersPipeOperator
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import TimeCyclesBinningPipeOperator
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import TimeIntervalsBinningPipeOperator
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import TimePhasesBinningPipeOperator
from tse_analytics.core.data.shared import Animal, Factor, GroupingMode, Variable
from tse_analytics.core.messaging.messages import (
    BinningMessage,
    DataChangedMessage,
    DatasetChangedMessage,
    GroupingModeChangedMessage,
)
from tse_analytics.core.messaging.messenger import Messenger
from tse_analytics.modules.phenomaster.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_analytics.modules.phenomaster.calo_details.data.calo_details import CaloDetails


class DataHub:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger

        self.selected_dataset: Dataset | None = None
        self.selected_factor: Factor | None = None
        self.selected_animals: list[Animal] = []
        self.selected_variables: list[Variable] = []

        self.grouping_mode = GroupingMode.ANIMALS

        self.binning_params = BinningParams(False, BinningMode.INTERVALS, BinningOperation.MEAN)
        self.outliers_params = OutliersParams(OutliersMode.OFF, 3.0)

        self.selected_variable = ""

    def clear(self):
        self.selected_dataset = None
        self.selected_factor = None
        self.selected_animals.clear()
        self.selected_variables.clear()
        QPixmapCache.clear()
        gc.collect()

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

    def set_grouping_mode(self, mode: GroupingMode):
        self.grouping_mode = mode
        self.messenger.broadcast(GroupingModeChangedMessage(self, self.grouping_mode))

    def set_selected_dataset(self, dataset: Dataset) -> None:
        # if self.selected_dataset is dataset:
        #     return
        self.selected_dataset = dataset
        self.selected_factor = None
        self.selected_animals.clear()
        self.selected_variables.clear()

        self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def set_selected_animals(self, animals: list[Animal]) -> None:
        self.selected_animals = animals
        self._broadcast_data_changed()

    def set_selected_factor(self, factor: Factor | None) -> None:
        self.selected_factor = factor
        self._broadcast_data_changed()

    def set_selected_variables(self, variables: list[Variable]) -> None:
        self.selected_variables = variables
        self._broadcast_data_changed()

    def _broadcast_data_changed(self):
        self.messenger.broadcast(DataChangedMessage(self))

    def adjust_dataset_time(self, indexes: list[QModelIndex], delta: str) -> None:
        if self.selected_dataset is not None:
            self.selected_dataset.adjust_time(delta)
            self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def export_to_excel(self, path: str) -> None:
        if self.selected_dataset is not None:
            with pd.ExcelWriter(path) as writer:
                self.get_current_df().to_excel(writer, sheet_name="Data")

    def export_to_csv(self, path: str) -> None:
        if self.selected_dataset is not None:
            self.get_current_df().to_csv(path, sep=";", index=False)

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

                    active_df.loc[
                        active_df[(active_df["Box"] == result.box_number) & (active_df["Bin"] == bin_number)].index[0],
                        ["O2-p", "CO2-p", "VO2(3)-p", "VCO2(3)-p", "RER-p", "H(3)-p"],
                    ] = [row["O2-p"], row["CO2-p"], row["VO2(3)-p"], row["VCO2(3)-p"], row["RER-p"], row["H(3)-p"]]

            if "O2-p" not in dataset.variables:
                dataset.variables["O2-p"] = Variable("O2-p", "[%]", "Predicted O2")
            if "CO2-p" not in dataset.variables:
                dataset.variables["CO2-p"] = Variable("CO2-p", "[%]", "Predicted CO2")
            if "VO2(3)-p" not in dataset.variables:
                dataset.variables["VO2(3)-p"] = Variable("VO2(3)-p", "[ml/h]", "Predicted VO2(3)")
            if "VCO2(3)-p" not in dataset.variables:
                dataset.variables["VCO2(3)-p"] = Variable("VCO2(3)-p", "[ml/h]", "Predicted VCO2(3)")
            if "RER-p" not in dataset.variables:
                dataset.variables["RER-p"] = Variable("RER-p", "", "Predicted RER")
            if "H(3)-p" not in dataset.variables:
                dataset.variables["H(3)-p"] = Variable("H(3)-p", "[kcal/h]", "Predicted H(3)")
            dataset.refresh_active_df()
            self.set_selected_dataset(dataset)

    def get_current_df(self, variables: list[str] | None = None, dropna=False) -> pd.DataFrame:
        if variables is not None:
            default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
            factor_columns = list(self.selected_dataset.factors.keys())
            result = self.selected_dataset.active_df[default_columns + factor_columns + variables].copy()
        else:
            result = self.selected_dataset.active_df.copy()

        # Filter operator
        if len(self.selected_animals) > 0:
            operator = AnimalFilterPipeOperator(self.selected_animals)
            result = operator.process(result)

        # Outliers operator
        if self.outliers_params.mode == OutliersMode.REMOVE:
            if variables is None:
                variables = list(self.selected_dataset.variables.keys())
            operator = OutliersPipeOperator(self.outliers_params, variables)
            result = operator.process(result)

        # # Error calculation operator
        # if calculate_error and self.selected_variable != "":
        #     operator = ErrorPipeOperator(self.selected_variable)
        #     result = operator.process(result)

        # Binning
        if self.binning_params.apply:
            factor_names = list(self.selected_dataset.factors.keys())
            match self.binning_params.mode:
                case BinningMode.INTERVALS:
                    operator = TimeIntervalsBinningPipeOperator(
                        self.selected_dataset.binning_settings.time_intervals_settings,
                        self.binning_params.operation,
                        self.grouping_mode,
                        factor_names,
                        self.selected_factor,
                    )
                    result = operator.process(result)
                case BinningMode.CYCLES:
                    operator = TimeCyclesBinningPipeOperator(
                        self.selected_dataset.binning_settings.time_cycles_settings,
                        self.binning_params.operation,
                        self.grouping_mode,
                        factor_names,
                        self.selected_factor,
                    )
                    result = operator.process(result)
                case BinningMode.PHASES:
                    operator = TimePhasesBinningPipeOperator(
                        self.selected_dataset.binning_settings.time_phases_settings,
                        self.binning_params.operation,
                        self.grouping_mode,
                        factor_names,
                        self.selected_factor,
                    )
                    result = operator.process(result)

        # TODO: should or should not?
        if dropna:
            result = result.dropna()

        return result

    def get_anova_df(self, variables: list[str] | None = None) -> pd.DataFrame:
        if variables is not None:
            default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]
            factor_columns = list(self.selected_dataset.factors.keys())
            result = self.selected_dataset.active_df[default_columns + factor_columns + variables].copy()
        else:
            result = self.selected_dataset.active_df.copy()

        # Filter operator
        if len(self.selected_animals) > 0:
            operator = AnimalFilterPipeOperator(self.selected_animals)
            result = operator.process(result)

        # Outliers operator
        if self.outliers_params.mode == OutliersMode.REMOVE:
            if variables is None:
                variables = list(self.selected_dataset.variables.keys())
            operator = OutliersPipeOperator(self.outliers_params, variables)
            result = operator.process(result)

        # Binning
        factor_names = list(self.selected_dataset.factors.keys())
        operator = TimeIntervalsBinningPipeOperator(
            TimeIntervalsBinningSettings("day", 365),
            BinningOperation.MEAN,
            GroupingMode.ANIMALS,
            factor_names,
            None,
        )
        result = operator.process(result)

        # TODO: should or should not?
        result = result.dropna()

        return result

    def get_bar_plot_df(self, variable: str) -> pd.DataFrame:
        default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin", variable]
        factor_columns = list(self.selected_dataset.factors.keys())
        result = self.selected_dataset.active_df[default_columns + factor_columns].copy()

        # Filter operator
        if len(self.selected_animals) > 0:
            operator = AnimalFilterPipeOperator(self.selected_animals)
            result = operator.process(result)

        # Outliers operator
        if self.outliers_params.mode == OutliersMode.REMOVE:
            operator = OutliersPipeOperator(self.outliers_params, [variable])
            result = operator.process(result)

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
                result.loc[result["DateTime"] >= phase.start_timestamp, "Bin"] = phase.name

            result["Bin"] = result["Bin"].astype("category")
            result.drop(columns=["DateTime"], inplace=True)

            # Sort category names by time
            categories = [item.name for item in self.selected_dataset.binning_settings.time_phases_settings.time_phases]
            result["Bin"] = result["Bin"].cat.set_categories(categories, ordered=True)

        return result
