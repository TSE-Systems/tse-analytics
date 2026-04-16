from tse_analytics.core.data.binning import BinningMode, BinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.operators.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.operators.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.operators.time_phases_binning_pipe_operator import process_time_phases_binning


def process_derived_table(
    datatable: Datatable,
    excluded_animal_ids: set[str],
    binning_mode: BinningMode,
    binning_settings: BinningSettings | None,
):
    # Exclude animals
    if len(excluded_animal_ids) > 0:
        datatable.exclude_animals(excluded_animal_ids)

    # Time binning
    if binning_settings is not None:
        match binning_mode:
            case BinningMode.INTERVALS:
                datatable.df = process_time_interval_binning(
                    datatable.df,
                    binning_settings.time_intervals_settings,
                    datatable.variables,
                    origin=datatable.dataset.experiment_started,
                )
            case BinningMode.CYCLES:
                datatable.df = process_time_cycles_binning(
                    datatable.df,
                    binning_settings.time_cycles_settings,
                    datatable.variables,
                )
            case BinningMode.PHASES:
                datatable.df = process_time_phases_binning(
                    datatable.df,
                    binning_settings.time_phases_settings,
                    datatable.variables,
                )
            case _:
                raise ValueError(f"Unsupported binning mode: {binning_mode}")
