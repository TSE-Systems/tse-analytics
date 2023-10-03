from typing import Optional

import pandas as pd

from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_datatools.analysis.pipeline.pipe_operator import PipeOperator
from tse_datatools.data.factor import Factor
from tse_datatools.data.time_intervals_binning_settings import TimeIntervalsBinningSettings


class TimeIntervalsBinningPipeOperator(PipeOperator):
    def __init__(
        self,
        settings: TimeIntervalsBinningSettings,
        binning_operation: BinningOperation,
        grouping_mode: GroupingMode,
        factor_names: list[str],
        selected_factor: Optional[Factor],
    ):
        self.settings = settings
        self.binning_operation = binning_operation
        self.grouping_mode = grouping_mode
        self.factor_names = factor_names
        self.selected_factor = selected_factor

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        # Store initial column order
        cols = df.columns

        result: Optional[pd.DataFrame] = None

        unit = "H"
        match self.settings.unit:
            case "day":
                unit = "D"
            case "hour":
                unit = "H"
            case "minute":
                unit = "min"
        timedelta = pd.Timedelta(f"{self.settings.delta}{unit}")

        match self.grouping_mode:
            case GroupingMode.ANIMALS:
                result = df.groupby(
                    ["Animal", "Box", "Run"] + self.factor_names, dropna=False, observed=False
                ).resample(timedelta, on="DateTime", origin="start")
            case GroupingMode.FACTORS:
                if self.selected_factor is not None:
                    result = df.groupby([self.selected_factor.name, "Run"], dropna=False, observed=False).resample(
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
                result.sort_values(by=["DateTime", "Box"], inplace=True)
            case GroupingMode.FACTORS:
                if self.selected_factor is not None:
                    result.sort_values(by=["DateTime", self.selected_factor.name], inplace=True)
            case GroupingMode.RUNS:
                result.sort_values(by=["DateTime", "Run"], inplace=True)

        # the inverse of groupby, reset_index
        result = result.reset_index().reindex(cols, axis=1)

        # Hide empty columns
        match self.grouping_mode:
            case GroupingMode.FACTORS:
                result.drop(columns=["Animal", "Box"], inplace=True)
            case GroupingMode.RUNS:
                result.drop(columns=["Animal", "Box"], inplace=True)

        start_date_time = result["DateTime"][0]
        result["Timedelta"] = result["DateTime"] - start_date_time

        result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)
        result = result.astype({"Bin": "category"})

        return result
