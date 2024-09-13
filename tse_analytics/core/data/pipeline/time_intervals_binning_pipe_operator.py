import pandas as pd

from tse_analytics.core.data.binning import BinningOperation, TimeIntervalsBinningSettings
from tse_analytics.core.data.shared import SplitMode

default_columns = ["DateTime", "Timedelta", "Animal", "Box", "Run", "Bin"]


def process_time_interval_binning(
    df: pd.DataFrame,
    settings: TimeIntervalsBinningSettings,
    binning_operation: BinningOperation,
    split_mode: SplitMode,
    factor_names: list[str],
    selected_factor_name: str | None,
) -> pd.DataFrame:
    if df.empty:
        return df

    agg = {
        "DateTime": "first",
        "Box": "first",
        "Run": "first",
    }
    for column in df.columns:
        if column not in default_columns:
            if df.dtypes[column].name != "category":
                agg[column] = binning_operation.value

    match split_mode:
        case SplitMode.ANIMAL:
            group_by = ["Animal"] + factor_names
            sort_by = ["Timedelta", "Box"]
            grouped = df.groupby(group_by, dropna=False, observed=False)
        case SplitMode.FACTOR:
            group_by = [selected_factor_name]
            sort_by = ["Timedelta", selected_factor_name]
            grouped = df.groupby(group_by, dropna=False, observed=False)
        case SplitMode.RUN:
            agg.pop("Run")
            group_by = ["Run"]
            sort_by = ["Timedelta", "Run"]
            grouped = df.groupby(group_by, dropna=False, observed=False)
        case _:  # Total split mode
            sort_by = ["Timedelta"]
            grouped = df

    timedelta = pd.Timedelta(f"{settings.delta}{settings.unit}")
    resampler = grouped.resample(timedelta, on="Timedelta", origin="start")
    result = resampler.agg(agg)

    result.sort_values(by=sort_by, inplace=True)

    # the inverse of groupby, reset_index
    result.reset_index(inplace=True)

    # start_date_time = result["DateTime"].iloc[0]
    # result["Timedelta"] = result["DateTime"] - start_date_time

    result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)
    # result = result.astype({"Bin": "category"})

    return result
