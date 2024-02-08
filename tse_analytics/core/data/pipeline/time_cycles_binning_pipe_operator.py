import pandas as pd

from tse_analytics.core.data.binning import BinningOperation, TimeCyclesBinningSettings
from tse_analytics.core.data.pipeline.pipe_operator import PipeOperator
from tse_analytics.core.data.shared import Factor, GroupingMode


class TimeCyclesBinningPipeOperator(PipeOperator):
    def __init__(
        self,
        settings: TimeCyclesBinningSettings,
        binning_operation: BinningOperation,
        grouping_mode: GroupingMode,
        factor_names: list[str],
        selected_factor: Factor | None,
    ):
        self.settings = settings
        self.binning_operation = binning_operation
        self.grouping_mode = grouping_mode
        self.factor_names = factor_names
        self.selected_factor = selected_factor

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        def filter_method(x):
            return "Light" if self.settings.light_cycle_start <= x.time() < self.settings.dark_cycle_start else "Dark"

        df["Bin"] = df["DateTime"].apply(filter_method).astype("category")
        df.drop(columns=["DateTime"], inplace=True)

        match self.grouping_mode:
            case GroupingMode.ANIMALS:
                group_by = ["Animal", "Box", "Bin"] + self.factor_names
            case GroupingMode.FACTORS:
                if self.selected_factor is not None:
                    group_by = [self.selected_factor.name, "Bin"]
            case GroupingMode.RUNS:
                group_by = ["Run", "Bin"]

        grouped = df.groupby(group_by, dropna=False, observed=True)

        match self.binning_operation:
            case BinningOperation.MEAN:
                result = grouped.mean(numeric_only=True)
            case BinningOperation.MEDIAN:
                result = grouped.median(numeric_only=True)
            case BinningOperation.SUM:
                result = grouped.sum(numeric_only=True)

        # the inverse of groupby, reset_index
        result = result.reset_index()

        return result
