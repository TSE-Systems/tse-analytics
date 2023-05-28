import gc
import timeit
from datetime import time
from typing import Optional

import numpy as np
import pandas as pd
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QPixmapCache

from tse_analytics.messaging.messages import (
    ClearDataMessage,
    DataChangedMessage,
    DatasetChangedMessage,
    GroupingModeChangedMessage,
)
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.views.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.analysis.binning_params import BinningParams
from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_datatools.analysis.outliers_params import OutliersParams
from tse_datatools.analysis.pipeline.time_cycles_pipe_operator import TimeCyclesPipeOperator, TimeCyclesParams
from tse_datatools.analysis.processor import calculate_grouped_data
from tse_datatools.data.animal import Animal
from tse_datatools.data.dataset import Dataset
from tse_datatools.data.factor import Factor
from tse_datatools.data.variable import Variable


class DataHub:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger

        self.selected_dataset: Optional[Dataset] = None
        self.selected_factor: Optional[Factor] = None
        self.selected_animals: list[Animal] = []
        self.selected_variables: list[Variable] = []

        self.grouping_mode = GroupingMode.ANIMALS

        self.binning_params = BinningParams(False, pd.Timedelta("1H"), BinningOperation.MEAN)
        self.outliers_params = OutliersParams(False, 3.0)
        self.time_cycles_params = TimeCyclesParams(False, time(7, 0), time(19, 0))

        self.selected_variable = ""

    def clear(self):
        self.selected_dataset = None
        self.selected_factor = None
        # self.apply_binning = False
        self.selected_animals.clear()
        self.selected_variables.clear()
        QPixmapCache.clear()
        gc.collect()

        self.messenger.broadcast(ClearDataMessage(self))

    def set_grouping_mode(self, mode: GroupingMode):
        self.grouping_mode = mode
        self.messenger.broadcast(GroupingModeChangedMessage(self, self.grouping_mode))

    def set_selected_dataset(self, dataset: Dataset) -> None:
        if self.selected_dataset is dataset:
            return
        self.selected_dataset = dataset
        self.selected_factor = None
        self.selected_animals.clear()
        self.selected_variables.clear()

        self.messenger.broadcast(DatasetChangedMessage(self, self.selected_dataset))

    def set_selected_animals(self, animals: list[Animal]) -> None:
        self.selected_animals = animals
        self._broadcast_data_changed()

    def set_selected_factor(self, factor: Optional[Factor]) -> None:
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

    def append_fitting_results(self, fitting_results: dict[int, CaloDetailsFittingResult]) -> None:
        if self.selected_dataset is not None:
            tic = timeit.default_timer()
            active_df = self.selected_dataset.active_df
            active_df["O2-p"] = np.NaN
            active_df["CO2-p"] = np.NaN
            active_df["RER-p"] = np.NaN
            active_df["H(3)-p"] = np.NaN
            for result in fitting_results.values():
                for index, row in result.df.iterrows():
                    bin_number = row["Bin"]

                    active_df['O2-p'] = np.where(
                        (active_df['Box'] == result.box_number) & (active_df["Bin"] == bin_number), row["O2-p"],
                        active_df['O2-p'])

                    active_df['CO2-p'] = np.where(
                        (active_df['Box'] == result.box_number) & (active_df["Bin"] == bin_number), row["CO2-p"],
                        active_df['CO2-p'])

                    active_df['RER-p'] = np.where(
                        (active_df['Box'] == result.box_number) & (active_df["Bin"] == bin_number), row["RER-p"],
                        active_df['RER-p'])

                    active_df['H(3)-p'] = np.where(
                        (active_df['Box'] == result.box_number) & (active_df["Bin"] == bin_number), row["H(3)-p"],
                        active_df['H(3)-p'])
            print(timeit.default_timer() - tic)

    def get_current_df(self, calculate_error=False) -> pd.DataFrame:
        result = self.selected_dataset.active_df.copy()

        factor_names = list(self.selected_dataset.factors.keys())

        timedelta = (
            self.selected_dataset.sampling_interval if not self.binning_params.apply else self.binning_params.timedelta
        )

        # Apply time cycles if needed
        result = TimeCyclesPipeOperator(self.time_cycles_params).process(result)

        if self.grouping_mode == GroupingMode.FACTORS and self.selected_factor is not None:
            result = calculate_grouped_data(
                result,
                timedelta,
                self.binning_params.operation,
                self.grouping_mode,
                factor_names,
                self.selected_variable if calculate_error else None,
                self.selected_factor,
            )
            # TODO: should or should not?
            # result = result.dropna()
        elif self.grouping_mode == GroupingMode.ANIMALS and len(self.selected_dataset.animals) > 0:
            if len(self.selected_animals) > 0:
                animal_ids = [animal.id for animal in self.selected_animals]
                result = result[result["Animal"].isin(animal_ids)]
            if self.binning_params.apply:
                result = calculate_grouped_data(
                    result,
                    timedelta,
                    self.binning_params.operation,
                    self.grouping_mode,
                    factor_names,
                    self.selected_variable if calculate_error else None,
                    self.selected_factor,
                )
        if self.grouping_mode == GroupingMode.RUNS:
            result = calculate_grouped_data(
                result,
                timedelta,
                self.binning_params.operation,
                self.grouping_mode,
                factor_names,
                self.selected_variable if calculate_error else None,
                self.selected_factor,
            )
            # TODO: should or should not?
            # result = result.dropna()

        return result
