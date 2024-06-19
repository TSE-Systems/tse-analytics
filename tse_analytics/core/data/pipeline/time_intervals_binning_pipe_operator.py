import pandas as pd

from tse_analytics.core.data.binning import BinningOperation, TimeIntervalsBinningSettings
from tse_analytics.core.data.pipeline.pipe_operator import PipeOperator
from tse_analytics.core.data.shared import Factor, SplitMode


class TimeIntervalsBinningPipeOperator(PipeOperator):
    def __init__(
        self,
        settings: TimeIntervalsBinningSettings,
        binning_operation: BinningOperation,
        grouping_mode: SplitMode,
        factor_names: list[str],
        selected_factor: Factor | None,
    ):
        self.settings = settings
        self.binning_operation = binning_operation
        self.grouping_mode = grouping_mode
        self.factor_names = factor_names
        self.selected_factor = selected_factor

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        match self.grouping_mode:
            case SplitMode.ANIMAL:
                group_by = ["Animal", "Box"] + self.factor_names
            case SplitMode.FACTOR:
                group_by = [self.selected_factor.name]
            case SplitMode.RUN:
                group_by = ["Run"]

        grouped = df.groupby(group_by, dropna=False, observed=False)

        timedelta = pd.Timedelta(f"{self.settings.delta}{self.settings.unit}")
        resampler = grouped.resample(timedelta, on="DateTime", origin="start")

        match self.binning_operation:
            case BinningOperation.MEAN:
                result = resampler.mean(numeric_only=True)
            case BinningOperation.MEDIAN:
                result = resampler.median(numeric_only=True)
            case BinningOperation.SUM:
                result = resampler.sum(numeric_only=True)

        match self.grouping_mode:
            case SplitMode.ANIMAL:
                sort_by = ["DateTime", "Animal"]
            case SplitMode.FACTOR:
                sort_by = ["DateTime", self.selected_factor.name]
            case SplitMode.RUN:
                sort_by = ["DateTime", "Run"]

        result.sort_values(by=sort_by, inplace=True)

        # the inverse of groupby, reset_index
        result = result.reset_index()

        start_date_time = result["DateTime"][0]
        result["Timedelta"] = result["DateTime"] - start_date_time

        result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)
        result = result.astype({"Bin": "category"})

        return result
