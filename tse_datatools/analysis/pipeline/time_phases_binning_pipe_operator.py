import pandas as pd

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
        selected_factor: Factor | None,
    ):
        self.settings = settings
        self.binning_operation = binning_operation
        self.grouping_mode = grouping_mode
        self.factor_names = factor_names
        self.selected_factor = selected_factor

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        self.settings.time_phases.sort(key=lambda x: x.start_timestamp)

        df["Bin"] = None
        for phase in self.settings.time_phases:
            df.loc[df["DateTime"] >= phase.start_timestamp, "Bin"] = phase.name

        df["Bin"] = df["Bin"].astype("category")
        df.drop(columns=["DateTime"], inplace=True)

        # Sort category names by time
        categories = [item.name for item in self.settings.time_phases]
        df["Bin"] = df["Bin"].cat.set_categories(categories, ordered=True)

        result: pd.DataFrame | None = None

        match self.grouping_mode:
            case GroupingMode.ANIMALS:
                result = df.groupby(["Animal", "Box", "Bin"] + self.factor_names, observed=True)
            case GroupingMode.FACTORS:
                if self.selected_factor is not None:
                    result = df.groupby([self.selected_factor.name, "Bin"], observed=True)
            case GroupingMode.RUNS:
                result = df.groupby(["Run", "Bin"], observed=True)

        match self.binning_operation:
            case BinningOperation.MEAN:
                result = result.mean(numeric_only=True)
            case BinningOperation.MEDIAN:
                result = result.median(numeric_only=True)
            case BinningOperation.SUM:
                result = result.sum(numeric_only=True)

        # match self.grouping_mode:
        #     case GroupingMode.ANIMALS:
        #         result.sort_values(by=["Bin", "Animal", "Box"], inplace=True)
        #     case GroupingMode.FACTORS:
        #         if self.selected_factor is not None:
        #             result.sort_values(by=["Bin", self.selected_factor.name], inplace=True)
        #     case GroupingMode.RUNS:
        #         result.sort_values(by=["Bin", "Run"], inplace=True)

        # the inverse of groupby, reset_index
        result = result.reset_index()

        return result
