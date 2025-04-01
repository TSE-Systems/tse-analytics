import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable

DATA_SUFFIX = "-IC"


class IntelliCageData:
    def __init__(
        self,
        dataset: "IntelliCageDataset",
        name: str,
        visits_df: pd.DataFrame,
        nosepokes_df: pd.DataFrame,
        environment_df: pd.DataFrame,
        hardware_events_df: pd.DataFrame,
        log_df: pd.DataFrame,
    ):
        self.dataset = dataset
        self.name = name

        self.visits_df = visits_df
        self.nosepokes_df = nosepokes_df
        self.environment_df = environment_df
        self.hardware_events_df = hardware_events_df
        self.log_df = log_df

        self.device_ids: list[int] = hardware_events_df["Cage"].unique().tolist()
        self.device_ids.sort()

    def get_visits_datatable(self) -> Datatable:
        df = self.visits_df.copy()

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
        if self.dataset.metadata["data_descriptor"]["Version"] == "Version1":
            df = pd.merge_asof(
                df,
                self.environment_df,
                on="DateTime",
                direction="nearest",
            )
        else:
            df = pd.merge_asof(
                df,
                self.environment_df,
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
        # Sort variables by name
        variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Add Timedelta column
        experiment_started = self.dataset.experiment_started
        df.insert(loc=3, column="Timedelta", value=df["DateTime"] - experiment_started)

        # Add Run column
        # df.insert(loc=4, column="Run", value=1)

        # Convert types
        df = df.astype({
            "Animal": "category",
            "PlaceError": "int",
        })

        datatable = Datatable(
            self.dataset,
            "Visits",
            "IntelliCage visits data",
            variables,
            df,
            None,
        )

        return datatable

    def get_nosepokes_datatable(self, visits_datatable: Datatable) -> Datatable:
        df = self.nosepokes_df.copy()
        visits_preprocessed_df = visits_datatable.original_df.copy()

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
        if self.dataset.metadata["data_descriptor"]["Version"] == "Version1":
            df = pd.merge_asof(
                df,
                self.environment_df,
                on="DateTime",
                direction="nearest",
            )
        else:
            df = pd.merge_asof(
                df,
                self.environment_df,
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
        # Sort variables by name
        variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Add Timedelta column
        experiment_started = self.dataset.experiment_started
        df.insert(loc=2, column="Timedelta", value=df["DateTime"] - experiment_started)

        # Add nosepoke-related columns to visits dataframe
        if self.dataset.metadata["data_descriptor"]["Version"] == "Version1":
            grouped_by_visit = df.groupby("VisitID").aggregate(
                NosepokesNumber=("VisitID", "size"),
                NosepokesDuration=("NosepokeDuration", "sum"),
                LicksNumber=("LickNumber", "sum"),
                LicksDuration=("LickDuration", "sum"),
                SideErrors=("SideError", "sum"),
                TimeErrors=("TimeError", "sum"),
                ConditionErrors=("ConditionError", "sum"),
            )
        else:
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
        visits_datatable.original_df = visits_datatable.original_df.join(grouped_by_visit, on="VisitID")
        visits_datatable.refresh_active_df()

        visits_datatable.variables = visits_datatable.variables | {
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
            "LicksDuration": Variable(
                "LicksDuration",
                "sec",
                "Licks duration",
                "float64",
                Aggregation.SUM,
                False,
            ),
        }

        if self.dataset.metadata["data_descriptor"]["Version"] != "Version1":
            visits_datatable.variables["LicksContactTime"] = Variable(
                "LicksContactTime",
                "sec",
                "Licks contact time",
                "float64",
                Aggregation.SUM,
                False,
            )


        datatable = Datatable(
            self.dataset,
            "Nosepokes",
            "IntelliCage nosepokes data",
            variables,
            df,
            None,
        )

        return datatable
