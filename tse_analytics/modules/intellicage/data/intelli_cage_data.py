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
        df = pd.merge(
            self.nosepokes_df.copy(),
            self.visits_df.copy(),
            on="VisitID",
            suffixes=("Nosepoke", "Visit"),
        )

        df[f"VisitDuration"] = (df["VisitEnd"] - df["VisitStart"]).dt.total_seconds()
        df[f"NosepokeDuration"] = (df["NosepokeEnd"] - df["NosepokeStart"]).dt.total_seconds()

        tag_to_animal_map = {}
        for animal in self.ic_dataset.animals.values():
            tag_to_animal_map[animal.text1] = animal.id

        # Replace animal tags with animal IDs
        df["AnimalTag"] = df["AnimalTag"].replace(tag_to_animal_map)

        df.rename(
            columns={
                "NosepokeStart": "DateTime",
                "AnimalTag": "Animal",
            },
            inplace=True,
        )

        df.drop(
            columns=[
                "NosepokeEnd",
            ],
            inplace=True,
        )

        # Set columns order
        # df = df[[
        #     "DateTime",
        #     f"Duration{DATA_SUFFIX}",
        #     "Animal",
        #     # "VisitID",
        #     # "Cage",
        #     # "Corner",
        #     # "CornerCondition",
        #     # "PlaceError",
        #     # "LickNumber",
        #     # "LickDuration",
        #     # "ModuleName",
        # ]]
        # default_columns = ["DateTime", "Animal"]
        # other_columns = [col for col in df.columns if col not in default_columns]
        # df = df[default_columns + other_columns]

        variables = {
            f"Duration{DATA_SUFFIX}": Variable(
                f"Duration{DATA_SUFFIX}",
                "sec",
                "AnimalGate session duration",
                "float64",
                Aggregation.MEAN,
                False,
            ),
        }

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # phases_old = df["ModuleName"][df["ModuleName"] != df["ModuleName"].shift()].values
        # shiftIDs = df[df["ModuleName"] != df["ModuleName"].shift()]["VisitID"].values

        return df, variables
