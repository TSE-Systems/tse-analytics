"""
Pipeline operator for time binning in a DataFrame.

This module provides a function for processing time binning in a DataFrame
based on the specified binning settings. It delegates to specific binning
functions based on the binning mode (intervals, cycles, or phases).
"""

import pandas as pd

from tse_analytics.core.data.binning import BinningMode, BinningSettings
from tse_analytics.core.data.operators.time_cycles_binning_pipe_operator import process_time_cycles_binning
from tse_analytics.core.data.operators.time_intervals_binning_pipe_operator import process_time_interval_binning
from tse_analytics.core.data.operators.time_phases_binning_pipe_operator import process_time_phases_binning
from tse_analytics.core.data.shared import Variable


def process_time_binning(
    df: pd.DataFrame,
    settings: BinningSettings,
    variables: dict[str, Variable],
    experiment_started: pd.Timestamp,
) -> pd.DataFrame:
    """
    Process time binning in a DataFrame based on the specified binning settings.

    This function applies time binning to the DataFrame according to the specified
    binning settings, delegating to specific binning functions based on the binning mode.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to process.
    settings : BinningSettings
        Settings for time binning, including the mode and specific settings for each mode.
    variables : dict[str, Variable]
        Dictionary mapping variable names to Variable objects.
    experiment_started : pd.Timestamp
        The timestamp when the experiment started.

    Returns
    -------
    pd.DataFrame
        A DataFrame with time binning applied.
    """
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
