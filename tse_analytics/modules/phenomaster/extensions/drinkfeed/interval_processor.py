import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.extensions.drinkfeed.drinkfeed_settings import DrinkFeedSettings


def process_drinkfeed_intervals(
    datatable: Datatable,
    settings: DrinkFeedSettings,
    diets_dict: dict[int, float],
) -> Datatable:
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

    variables = datatable.variables.copy()

    for variable in datatable.variables.values():
        # Add caloric value column
        if "Feed" in variable.name:
            intervals_df = _add_caloric_column(intervals_df, variable.name, diets_dict, variables)

    # Sort by Timedelta column
    # intervals_df = intervals_df.sort_values(by=["Timedelta", "Animal"]).reset_index(drop=True)

    intervals_datatable = Datatable(
        datatable.dataset,
        "DrinkFeedIntervals",
        "Drink/Feed intervals datatable",
        variables,
        intervals_df,
        {
            "origin": "DrinkFeedIntervals",
            "samping_interval": timedelta,
        },
    )

    return intervals_datatable


def _add_caloric_column(
    df: pd.DataFrame,
    origin_column: str,
    diets_dict: dict[int, float],
    variables: dict[str, Variable],
) -> pd.DataFrame:
    if origin_column in df.columns:
        new_name = f"{origin_column}[kcal]"
        df.insert(
            df.columns.get_loc(origin_column) + 1,
            new_name,
            df["Animal"].astype("string"),
        )
        df = df.replace({new_name: diets_dict})
        df[new_name] = df[new_name].astype("Float64")
        df[new_name] = df[new_name] * df[origin_column]

        variable = Variable(
            new_name,
            "kcal",
            f"{variables[origin_column].name} caloric value",
            "Float64",
            variables[origin_column].aggregation,
            False,
        )
        variables[new_name] = variable
    return df
