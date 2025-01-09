import pandas as pd


class AnimalGateData:
    def __init__(
        self,
        im_dataset,
        name: str,
        sessions_df: pd.DataFrame,
        antenna_df: pd.DataFrame,
        log_df: pd.DataFrame,
        input_df: pd.DataFrame,
        output_df: pd.DataFrame,
    ):
        self.im_dataset = im_dataset
        self.name = name

        self.sessions_df = sessions_df
        self.antenna_df = antenna_df
        self.log_df = log_df
        self.input_df = input_df
        self.output_df = output_df
