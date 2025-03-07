import pandas as pd

from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.intellicage.data.intellicage_raw_data import IntelliCageRawData

DATA_SUFFIX = "-IC"


class IntelliCageData:
    def __init__(
        self,
        dataset,
        name: str,
        raw_data: IntelliCageRawData,
    ):
        self.dataset = dataset
        self.name = name
        self.raw_data = raw_data

        self.visits_df, self.visits_variables = self._preprocess_visits_df()
        self.nosepokes_df, self.nosepokes_variables = self._preprocess_nosepokes_df()

    def _preprocess_visits_df(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.raw_data.visits_df.copy()

        # Replace animal tags with animal IDs
        tag_to_animal_map = {}
        for animal in self.dataset.animals.values():
            tag_to_animal_map[animal.properties["Tag"]] = animal.id
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
            self.raw_data.environment_df,
            on="DateTime",
            by="Cage",
            direction="nearest",
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
        experiment_started = self.dataset.experiment_started
        df.insert(loc=3, column="Timedelta", value=df["DateTime"] - experiment_started)

        return df, variables

    def _preprocess_nosepokes_df(self) -> tuple[pd.DataFrame, dict[str, Variable]]:
        df = self.raw_data.nosepokes_df.copy()
        visits_preprocessed_df = self.visits_df.copy()

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
            self.raw_data.environment_df,
            on="DateTime",
            by="Cage",
            direction="nearest",
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
        experiment_started = self.dataset.experiment_started
        df.insert(loc=2, column="Timedelta", value=df["DateTime"] - experiment_started)

        # Add nosepoke-related columns to visits dataframe
        grouped_by_visit = df.groupby("VisitID").aggregate(
            NosepokesNumber=("VisitID", "size"),
            NosepokesDuration=("NosepokeDuration", "sum"),
            LicksNumber=("LickNumber", "sum"),
            LicksContactTime=("LickContactTime", "sum"),
            LicksDuration=("LickDuration", "sum"),
            SideErrors=("SideError", "sum"),
            TimeErrors=("TimeError", "sum"),
            ConditionErrors=("ConditionError", "sum"),
        )
        self.visits_df = self.visits_df.join(grouped_by_visit, on="VisitID")

        self.visits_variables = self.visits_variables | {
            "NosepokesNumber": Variable(
                "NosepokesNumber",
                "count",
                "Number of nosepokes",
                "int64",
                Aggregation.SUM,
                False,
            ),
            "NosepokesDuration": Variable(
                "NosepokesDuration",
                "sec",
                "Duration of nosepokes",
                "float64",
                Aggregation.SUM,
                False,
            ),
            "SideErrors": Variable(
                "SideErrors",
                "count",
                "Number of side errors",
                "int64",
                Aggregation.SUM,
                False,
            ),
            "TimeErrors": Variable(
                "TimeErrors",
                "count",
                "Number of time errors",
                "int64",
                Aggregation.SUM,
                False,
            ),
            "ConditionErrors": Variable(
                "ConditionErrors",
                "count",
                "Number of condition errors",
                "int64",
                Aggregation.SUM,
                False,
            ),
            "LicksNumber": Variable(
                "LicksNumber",
                "count",
                "Number of licks",
                "int64",
                Aggregation.SUM,
                False,
            ),
            "LicksContactTime": Variable(
                "LicksContactTime",
                "sec",
                "Licks contact time",
                "float64",
                Aggregation.SUM,
                False,
            ),
            "LicksDuration": Variable(
                "LicksDuration",
                "sec",
                "Licks duration",
                "float64",
                Aggregation.SUM,
                False,
            ),
        }

        return df, variables
