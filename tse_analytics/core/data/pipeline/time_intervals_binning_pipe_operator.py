import pandas as pd

from tse_analytics.core.data.binning import BinningOperation, TimeIntervalsBinningSettings
from tse_analytics.core.data.pipeline.pipe_operator import PipeOperator
from tse_analytics.core.data.shared import Factor, GroupingMode


class TimeIntervalsBinningPipeOperator(PipeOperator):
    def __init__(
        self,
        settings: TimeIntervalsBinningSettings,
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
        result: pd.DataFrame | None = None

        timedelta = pd.Timedelta(f"{self.settings.delta}{self.settings.unit}")

        match self.grouping_mode:
            case GroupingMode.ANIMALS:
                result = df.groupby(["Animal", "Box"] + self.factor_names, dropna=False, observed=False).resample(
                    timedelta, on="DateTime", origin="start"
                )
            case GroupingMode.FACTORS:
                if self.selected_factor is not None:
                    result = df.groupby([self.selected_factor.name], dropna=False, observed=False).resample(
                        timedelta, on="DateTime", origin="start"
                    )
            case GroupingMode.RUNS:
                result = df.groupby(["Run"], dropna=False, observed=False).resample(
                    timedelta, on="DateTime", origin="start"
                )

        match self.binning_operation:
            case BinningOperation.MEAN:
                result = result.mean(numeric_only=True)
            case BinningOperation.MEDIAN:
                result = result.median(numeric_only=True)
            case BinningOperation.SUM:
                result = result.sum(numeric_only=True)

        match self.grouping_mode:
            case GroupingMode.ANIMALS:
                result.sort_values(by=["DateTime", "Animal"], inplace=True)
            case GroupingMode.FACTORS:
                if self.selected_factor is not None:
                    result.sort_values(by=["DateTime", self.selected_factor.name], inplace=True)
            case GroupingMode.RUNS:
                result.sort_values(by=["DateTime", "Run"], inplace=True)

        # the inverse of groupby, reset_index
        result = result.reset_index()

        start_date_time = result["DateTime"][0]
        result["Timedelta"] = result["DateTime"] - start_date_time

        result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)
        result = result.astype({"Bin": "category"})

        return result
