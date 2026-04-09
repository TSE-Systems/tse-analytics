import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.modules.phenomaster.extensions.drinkfeed.drinkfeed_settings import DrinkFeedSettings


def process_drinkfeed_intervals(
    datatable: Datatable,
    settings: DrinkFeedSettings,
    diets_dict: dict[int, float],
):
    # TODO: drop unnecessary rows
    # long_df = long_df.loc[~(long_df["Value"] == 0)]

    grouped = datatable.df.groupby(["Animal"], dropna=False, observed=False)

    timedelta = pd.Timedelta(
        hours=settings.fixed_interval.hour,
        minutes=settings.fixed_interval.minute,
        seconds=settings.fixed_interval.second,
    )

    agg = {}
    for variable in datatable.variables.values():
        agg[variable.name] = variable.aggregation

    intervals_df = grouped.resample(
        timedelta,
        on="Timedelta",
        origin=datatable.dataset.experiment_started,
    ).aggregate(agg)

    intervals_df = intervals_df.sort_values(by=["Timedelta", "Animal"]).reset_index()

    # Insert Bin column
    intervals_df.insert(
        intervals_df.columns.get_loc("Timedelta") + 1,
        "Bin",
        (intervals_df["Timedelta"] / timedelta).round().astype("UInt64"),
    )

    # Add caloric value column
    for variable in datatable.variables.values():
        if "Feed" in variable.name:
            _add_caloric_column(intervals_df, variable.name, diets_dict)

    # Sort by Timedelta column
    # intervals_df = intervals_df.sort_values(by=["Timedelta", "Animal"]).reset_index(drop=True)

    return intervals_df


def _add_caloric_column(df: pd.DataFrame, origin_column: str, diets_dict: dict[int, float]) -> pd.DataFrame:
    if origin_column in df.columns:
        df.insert(df.columns.get_loc(origin_column) + 1, f"{origin_column}-kcal", df["Animal"].astype("string"))
        df.replace({f"{origin_column}-kcal": diets_dict}, inplace=True)
        df[f"{origin_column}-kcal"] = df[f"{origin_column}-kcal"].astype("Float64")
        df[f"{origin_column}-kcal"] = df[f"{origin_column}-kcal"] * df[origin_column]
    return df
