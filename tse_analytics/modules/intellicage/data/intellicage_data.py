import numpy as np
import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable


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
        df["VisitDuration"] = (df["End"] - df["Start"]).dt.total_seconds()

        # Add a visit number column for further binning (each visit as 1)
        df["VisitNumber"] = 1

        # Rename columns
        df.rename(
            columns={
                "Start": "DateTime",
            },
            inplace=True,
        )

        # Drop the non-necessary columns
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
            "VisitNumber": Variable(
                "VisitNumber",
                "count",
                "Visit number",
                "int",
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
            "AntennaNumber": Variable(
                "AntennaNumber",
                "count",
                "Antenna number",
                "int",
                Aggregation.SUM,
                False,
            ),
            "AntennaDuration": Variable(
                "AntennaDuration",
                "sec",
                "Antenna duration",
                "float64",
                Aggregation.SUM,
                False,
            ),
            "PresenceNumber": Variable(
                "PresenceNumber",
                "count",
                "Presence number",
                "int",
                Aggregation.SUM,
                False,
            ),
            "PresenceDuration": Variable(
                "PresenceDuration",
                "sec",
                "Presence duration",
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
            "PlaceError": Variable(
                "PlaceError",
                "count",
                "Place error",
                "bool",
                Aggregation.SUM,
                False,
            ),
        }

        df.sort_values(["DateTime"], inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Add Timedelta column
        experiment_started = self.dataset.experiment_started
        df.insert(loc=3, column="Timedelta", value=df["DateTime"] - experiment_started)

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
        df["NosepokeDuration"] = (df["End"] - df["Start"]).dt.total_seconds()

        # Add a nosepoke number column for further binning (each nosepoke as 1)
        df["NosepokeNumber"] = 1

        # Drop the non-necessary columns
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
            "NosepokeNumber": Variable(
                "NosepokeNumber",
                "count",
                "Nosepoke number",
                "int",
                Aggregation.SUM,
                False,
            ),
            "NosepokeDuration": Variable(
                "NosepokeDuration",
                "sec",
                "Nosepoke duration",
                "float64",
                Aggregation.MEAN,
                False,
            ),
            "PlaceError": Variable(
                "PlaceError",
                "count",
                "Place error",
                "bool",
                Aggregation.SUM,
                False,
            ),
            "SideError": Variable(
                "SideError",
                "count",
                "Side error",
                "bool",
                Aggregation.SUM,
                False,
            ),
            "TimeError": Variable(
                "TimeError",
                "count",
                "Time error",
                "bool",
                Aggregation.SUM,
                False,
            ),
            "ConditionError": Variable(
                "ConditionError",
                "count",
                "Condition error",
                "bool",
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
            "LickNumber": Variable(
                "LickNumber",
                "count",
                "Number of licks",
                "int64",
                Aggregation.SUM,
                False,
            ),
            "LickDuration": Variable(
                "LickDuration",
                "sec",
                "Licks duration",
                "float64",
                Aggregation.SUM,
                False,
            ),
        }

        if self.dataset.metadata["data_descriptor"]["Version"] != "Version1":
            visits_datatable.variables["LicksContactTime"] = Variable(
                "LickContactTime",
                "sec",
                "Lick contact time",
                "float64",
                Aggregation.SUM,
                False,
            )

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

        # Sort visits variables by name
        visits_datatable.variables = dict(sorted(visits_datatable.variables.items(), key=lambda x: x[0].lower()))

        # Convert types
        df = df.astype({
            # "Animal": "category",
            "SideError": np.int64,
            "TimeError": np.int64,
            "DoorState": np.int64,
            "AirState": np.int64,
            "ConditionError": np.int64,
        })

        datatable = Datatable(
            self.dataset,
            "Nosepokes",
            "IntelliCage nosepokes data",
            variables,
            df,
            None,
        )

        return datatable
