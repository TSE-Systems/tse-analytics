import pandas as pd

from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import ByTimeIntervalConfig

default_columns = ["Animal", "Timedelta", "DateTime", "Run"]


def process_table(
    datatable: Datatable,
    excluded_animal_ids: set[str],
    time_intervals_settings: TimeIntervalsBinningSettings | None,
):
    # Exclude animals
    if len(excluded_animal_ids) > 0:
        datatable.exclude_animals(excluded_animal_ids)

    # Time binning
    if time_intervals_settings is not None:
        df = datatable.df
        if df.empty:
            return df

        timedelta = pd.Timedelta(f"{time_intervals_settings.delta}{time_intervals_settings.unit}")

        agg = {
            "DateTime": "first",
        }

        include_runs = "Run" in df.columns
        if include_runs:
            agg["Run"] = "first"

        for column in df.columns:
            if column not in default_columns:
                if df.dtypes[column].name != "category":
                    if column in datatable.variables:
                        agg[column] = datatable.variables[column].aggregation
                else:
                    # Include categorical data fields
                    agg[column] = "first"

        result = df.groupby("Animal", dropna=False, observed=False)
        result = result.resample(timedelta, on="Timedelta", origin=datatable.dataset.experiment_started).aggregate(agg)

        result = result[result["DateTime"].notna()]

        result.reset_index(inplace=True, drop=False)

        # TODO: check if done properly: align timedelta to the resampling resolution
        result["Timedelta"] = result["Timedelta"].dt.round(timedelta)

        # Drop any prior Bin column; the factor system re-materializes it below.
        result.drop(columns=["Bin"], inplace=True, errors="ignore")
        result.sort_values(by=["Timedelta", "Animal"], inplace=True)
        result.reset_index(inplace=True, drop=True)

        if include_runs:
            result = result.astype({
                "Run": "UInt8",
            })

        datatable.metadata["sample_interval"] = timedelta
        datatable.df = result

        # Sync the dataset's "Bin" factor interval and re-apply factors so the
        # Bin column reflects the new binning.
        dataset = datatable.dataset
        bin_factor = dataset.factors.get("Bin")
        if bin_factor is not None and isinstance(bin_factor.config, ByTimeIntervalConfig):
            bin_factor.config.interval = timedelta.to_pytimedelta()
        datatable.set_factors(dataset.factors)
