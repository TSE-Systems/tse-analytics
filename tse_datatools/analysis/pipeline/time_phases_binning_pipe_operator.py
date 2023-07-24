from typing import Optional

import pandas as pd
import numpy as np

from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_datatools.analysis.pipeline.pipe_operator import PipeOperator
from tse_datatools.data.factor import Factor
from tse_datatools.data.time_phases_binning_settings import TimePhasesBinningSettings


class TimePhasesBinningPipeOperator(PipeOperator):
    def __init__(
        self,
        settings: TimePhasesBinningSettings,
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
        self.settings.time_phases.sort(key=lambda x: x.start_timestamp)

        df["Bin"] = np.NaN
        for phase in self.settings.time_phases:
            df.loc[df["DateTime"] >= phase.start_timestamp, "Bin"] = phase.name

        df["Bin"] = df["Bin"].astype("category")

        return df
