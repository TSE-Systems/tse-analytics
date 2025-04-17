import pandas as pd

from tse_analytics.core.data.binning import BinningMode, BinningSettings
from tse_analytics.core.data.pipeline.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.pipeline.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.pipeline.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.shared import Variable


def process_time_binning(
    df: pd.DataFrame,
    settings: BinningSettings,
    variables: dict[str, Variable],
    experiment_started: pd.Timestamp,
) -> pd.DataFrame:
    if settings.apply:
        match settings.mode:
            case BinningMode.INTERVALS:
                return process_time_interval_binning(
                    df,
                    settings.time_intervals_settings,
                    variables,
                    origin=experiment_started,
                )
            case BinningMode.CYCLES:
                return process_time_cycles_binning(
                    df,
                    settings.time_cycles_settings,
                    variables,
                )
            case BinningMode.PHASES:
                return process_time_phases_binning(
                    df,
                    settings.time_phases_settings,
                    variables,
                )
    return df
