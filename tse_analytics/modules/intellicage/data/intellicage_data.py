import numpy as np
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

        self.visits_preprocessed_df: pd.DataFrame | None = None
        self.nosepokes_preprocessed_df: pd.DataFrame | None = None

    def preprocess_data(self) -> dict[str, Variable]:
        self.visits_preprocessed_df, visits_variables = self._preprocess_visits_df()
        self.nosepokes_preprocessed_df, nosepokes_variables = self._preprocess_nosepokes_df()
        return visits_variables

    def _preprocess_visits_df(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.visits_df.copy()

        # Replace animal tags with animal IDs
        tag_to_animal_map = {}
        for animal in self.ic_dataset.animals.values():
            tag_to_animal_map[animal.tag] = animal.id
        df["AnimalTag"] = df["AnimalTag"].replace(tag_to_animal_map)
        df.rename(
            columns={
                "AnimalTag": "Animal",
            },
            inplace=True,
        )

        # Add duration column
        df[f"VisitDuration"] = (df["End"] - df["Start"]).dt.total_seconds()

        # Rename columns
        df.rename(
            columns={
                "Start": "DateTime",
            },
            inplace=True,
        )

        # Drop non-necessary columns
        df.drop(
            columns=[
                "End",
            ],
            inplace=True,
        )

        # Add temperature and illumination
        df = pd.merge_asof(
            df,
            self.environment_df.copy(),
            on="DateTime",
            by="Cage",
        )

        variables = {
            "PlaceError": Variable(
                "PlaceError",
                "count",
                "Place error",
                "bool",
                Aggregation.SUM,
                False,
            ),
            "VisitDuration": Variable(
                "VisitDuration",
                "sec",
                "Visit duration",
                "float64",
                Aggregation.SUM,
                False,
            ),
            "Temperature": Variable(
                "Temperature",
                "°C",
                "Cage temperature",
                "float64",
                Aggregation.MEAN,
                False,
            ),
            "Illumination": Variable(
                "Illumination",
                "",
                "Cage illumination",
                "float64",
                Aggregation.MEAN,
                False,
            ),
        }

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Add Timedelta column
        experiment_started = self.ic_dataset.experiment_started
        df.insert(loc=3, column="Timedelta", value=df["DateTime"] - experiment_started)

        return df, variables

    def _preprocess_nosepokes_df(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.nosepokes_df.copy()
        visits_preprocessed_df = self.visits_preprocessed_df.copy()

        # Sanitize visits table before merging
        visits_preprocessed_df.drop(
            columns=[
                "Timedelta",
                "Temperature",
                "Illumination",
            ],
            inplace=True,
        )

        visits_preprocessed_df.rename(
            columns={
                "DateTime": "VisitStart",
            },
            inplace=True,
        )

        # Add duration column
        df[f"NosepokeDuration"] = (df["End"] - df["Start"]).dt.total_seconds()

        # Drop non-necessary columns
        df.drop(
            columns=[
                "End",
            ],
            inplace=True,
        )

        df.rename(
            columns={
                "Start": "DateTime",
            },
            inplace=True,
        )

        df = pd.merge(
            df,
            visits_preprocessed_df,
            on="VisitID",
            suffixes=("Nosepoke", "Visit"),
        )

        # Add temperature and illumination
        df = pd.merge_asof(
            df,
            self.environment_df.copy(),
            on="DateTime",
            by="Cage",
        )

        variables = {
            "NosepokeDuration": Variable(
                "NosepokeDuration",
                "sec",
                "Nosepoke duration",
                "float64",
                Aggregation.MEAN,
                False,
            ),
        }

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Add Timedelta column
        experiment_started = self.ic_dataset.experiment_started
        df.insert(loc=2, column="Timedelta", value=df["DateTime"] - experiment_started)

        grouped_by_visit = df.groupby("VisitID").aggregate(
            Nosepokes=("VisitID", "size"),
            NosepokesDuration=("NosepokeDuration", "sum"),
            SideErrors=("SideError", "sum"),
            TimeErrors=("TimeError", "sum"),
            ConditionErrors=("ConditionError", "sum"),
            LicksNumber=("LickNumber", "sum"),
            LicksContactTime=("LickContactTime", "sum"),
            LicksDuration=("LickDuration", "sum"),
        )

        self.visits_preprocessed_df = self.visits_preprocessed_df.join(grouped_by_visit, on="VisitID")

        return df, variables
