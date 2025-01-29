import pandas as pd


class IntelliCageRawData:
    def __init__(
        self,
        visits_df: pd.DataFrame,
        nosepokes_df: pd.DataFrame,
        environment_df: pd.DataFrame,
        hardware_events_df: pd.DataFrame,
        log_df: pd.DataFrame,
    ):
        self.device_ids: list[int] = environment_df["Cage"].unique().tolist()
        self.device_ids.sort()

        self.visits_df = visits_df
        self.nosepokes_df = nosepokes_df
        self.environment_df = environment_df
        self.hardware_events_df = hardware_events_df
        self.log_df = log_df
