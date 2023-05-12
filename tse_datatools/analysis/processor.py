from typing import Optional

import pandas as pd

from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_datatools.analysis.binning_operation import BinningOperation
from tse_datatools.data.factor import Factor


def calculate_grouped_data(
    df: pd.DataFrame,
    timedelta: pd.Timedelta,
    operation: BinningOperation,
    grouping_mode: GroupingMode,
    factor_names: list[str],
    selected_variable: Optional[str] = None,
    selected_factor: Optional[Factor] = None,
) -> pd.DataFrame:
    # Store initial column order
    cols = df.columns

    result: Optional[pd.DataFrameGroupBy] = None
    match grouping_mode:
        case GroupingMode.FACTORS:
            if selected_factor is not None:
                result = df.groupby([selected_factor.name, "Run"]).resample(timedelta, on="DateTime", origin="start")
        case GroupingMode.ANIMALS:
            result = df.groupby(["Animal", "Box", "Run"] + factor_names).resample(timedelta, on="DateTime", origin="start")
        case GroupingMode.RUNS:
            result = df.groupby(["Run"]).resample(timedelta, on="DateTime", origin="start")

    errors = result.std(numeric_only=True)[selected_variable].to_numpy() if selected_variable is not None else None

    match operation:
        case BinningOperation.MEAN:
            result = result.mean(numeric_only=True)
        case BinningOperation.MEDIAN:
            result = result.median(numeric_only=True)
        case _:
            result = result.sum(numeric_only=True)

    match grouping_mode:
        case GroupingMode.FACTORS:
            if selected_factor is not None:
                result.sort_values(by=["DateTime", selected_factor.name], inplace=True)
        case GroupingMode.ANIMALS:
            result.sort_values(by=["DateTime", "Box"], inplace=True)
        case GroupingMode.RUNS:
            result.sort_values(by=["DateTime", "Run"], inplace=True)

    # the inverse of groupby, reset_index
    result = result.reset_index().reindex(cols, axis=1)

    # Hide empty columns
    match grouping_mode:
        case GroupingMode.FACTORS:
            result.drop(columns=["Animal", "Box"], inplace=True)
        case GroupingMode.RUNS:
            result.drop(columns=["Animal", "Box"], inplace=True)

    start_date_time = result["DateTime"][0]
    result["Timedelta"] = result["DateTime"] - start_date_time
    result["Bin"] = (result["Timedelta"] / timedelta).round().astype(int)

    if errors is not None:
        result["Std"] = errors

    # convert categorical types
    result = result.astype({
        "Bin": "category"
    })

    return result


def find_outliers_iqr(df: pd.DataFrame, extreme=False):
    q1 = df.quantile(0.25)
    q3 = df.quantile(0.75)
    iqr = q3 - q1
    coef = 3.0 if extreme else 1.5
    outliers = df[((df < (q1 - coef * iqr)) | (df > (q3 + coef * iqr)))]
    return outliers
