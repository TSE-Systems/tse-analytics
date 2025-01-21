import pandas as pd

from tse_analytics.core.data.shared import Aggregation, Variable

DATA_SUFFIX = "-IC"


class IntelliCageData:
    def __init__(
        self,
        ic_dataset,
        name: str,
        visits_df: pd.DataFrame,
        nosepokes_df: pd.DataFrame,
        environment_df: pd.DataFrame,
        hardware_events_df: pd.DataFrame,
        log_df: pd.DataFrame,
    ):
        self.ic_dataset = ic_dataset
        self.name = name
        self.device_ids: list[int] = environment_df["Cage"].unique().tolist()
        self.device_ids.sort()

        self.visits_df = visits_df
        self.nosepokes_df = nosepokes_df
        self.environment_df = environment_df
        self.hardware_events_df = hardware_events_df
        self.log_df = log_df

    def get_preprocessed_data(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.visits_df.copy()

        df[f"Duration{DATA_SUFFIX}"] = (df["End"] - df["Start"]).dt.total_seconds()

        tag_to_animal_map = {}
        for animal in self.ic_dataset.animals.values():
            tag_to_animal_map[animal.text1] = animal.id

        # Replace animal tags with animal IDs
        df["Tag"] = df["Tag"].replace(tag_to_animal_map)

        df.rename(
            columns={
                "Start": "DateTime",
                "Tag": "Animal",
                "Weight": f"Weight{DATA_SUFFIX}",
            },
            inplace=True,
        )

        df.drop(
            columns=[
                "DeviceId",
                "Direction",
                "End",
                "IdSectionVisited",
                "StandbySectionVisited",
            ],
            inplace=True,
        )

        # Set columns order
        df = df[["DateTime", "Animal", f"Duration{DATA_SUFFIX}", f"Weight{DATA_SUFFIX}"]]

        variables = {
            f"Duration{DATA_SUFFIX}": Variable(
                f"Duration{DATA_SUFFIX}",
                "sec",
                "AnimalGate session duration",
                "float64",
                Aggregation.MEAN,
                False,
            ),
            f"Weight{DATA_SUFFIX}": Variable(
                f"Weight{DATA_SUFFIX}",
                "g",
                "AnimalGate weight",
                "float64",
                Aggregation.MEAN,
                False,
            ),
        }

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df, variables
