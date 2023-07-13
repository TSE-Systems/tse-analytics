from typing import Optional

import pandas as pd

from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_datatools.analysis.pipeline.pipe_operator import PipeOperator
from tse_datatools.data.factor import Factor
from tse_datatools.data.time_cycles_binning_settings import TimeCyclesBinningSettings


class TimeCyclesBinningPipeOperator(PipeOperator):
    def __init__(
        self,
        settings: TimeCyclesBinningSettings,
        binning_operation: BinningOperation,
        grouping_mode: GroupingMode,
        factor_names: list[str],
        selected_factor: Optional[Factor]
    ):
        self.settings = settings
        self.binning_operation = binning_operation
        self.grouping_mode = grouping_mode
        self.factor_names = factor_names
        self.selected_factor = selected_factor

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        filter_method = (
            lambda x: "Light" if (self.settings.light_cycle_start <= x.time() < self.settings.dark_cycle_start) else "Dark"
        )
        df["Bin"] = df["DateTime"].apply(filter_method).astype("category")
        return df
