from tse_analytics.core.data.binning import BinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings
from tse_analytics.core.data.operators.time_binning_pipe_operator import process_time_binning


def process_derived_table(
    datatable: Datatable,
    excluded_animal_ids: set[str],
    binning_settings: BinningSettings,
    grouping_settings: GroupingSettings,
):
    # Exclude animals
    if len(excluded_animal_ids) > 0:
        datatable.exclude_animals(excluded_animal_ids)

    # Time binning
    if binning_settings.apply:
        datatable.df = process_time_binning(
            datatable.df,
            binning_settings,
            datatable.variables,
            datatable.dataset.experiment_started,
        )

    # Grouping
    if grouping_settings.mode != GroupingMode.ANIMAL:
        # No grouping needed in ANIMAL mode

        match grouping_settings.mode:
            case GroupingMode.FACTOR:
                group_by = ["Bin", grouping_settings.factor_name]
            case GroupingMode.RUN:
                group_by = ["Bin", "Run"]
            case _:  # Total split mode
                group_by = ["Bin"]

        aggregation = {}

        if "DateTime" in datatable.df.columns:
            aggregation["DateTime"] = "first"

        if "Timedelta" in datatable.df.columns:
            aggregation["Timedelta"] = "first"

        # TODO: use means only when aggregating in split modes!
        for variable in datatable.variables.values():
            aggregation[variable.name] = "mean"

        datatable.df = datatable.df.groupby(group_by, dropna=False, observed=False).aggregate(aggregation)
        datatable.df.reset_index(inplace=True)
