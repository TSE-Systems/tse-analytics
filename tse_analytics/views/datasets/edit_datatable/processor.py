from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.operators.time_intervals_binning_pipe_operator import process_time_interval_binning


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
        datatable.df = process_time_interval_binning(
            datatable.df,
            time_intervals_settings,
            datatable.variables,
            origin=datatable.dataset.experiment_started,
        )
