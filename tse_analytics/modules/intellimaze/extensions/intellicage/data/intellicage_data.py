import numpy as np
import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.modules.intellimaze.data.extension_data import ExtensionData


EXTENSION_NAME = "IntelliCage"


class IntelliCageData(ExtensionData):
    def __init__(
        self,
        dataset: "IntelliMazeDataset",
        name: str,
        raw_data: dict[str, pd.DataFrame],
    ):
        super().__init__(
            dataset,
            name,
            raw_data,
            dataset.devices[EXTENSION_NAME],
        )

    def preprocess_data(self) -> None:
        visits_datatable = self._get_visits_datatable()
        self.dataset.add_datatable(visits_datatable)

        nosepokes_datatable = self._get_nosepokes_datatable(visits_datatable)
        self.dataset.add_datatable(nosepokes_datatable)

    def _get_visits_datatable(self) -> Datatable:
        """
        Process raw visit data into a structured Datatable.

        This method processes the raw 'Visits' data from IntelliCage experiments,
        performing the following operations:
        - Replacing animal tags with animal IDs
        - Adding visit duration information
        - Adding visit number for counting
        - Merging with environmental data (temperature and illumination)
        - Creating a structured Datatable with defined variables and factors

        Returns
        -------
        Datatable
            A structured datatable containing processed visit data.
        """
        df = self.raw_data["Visits"].copy()

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
        df = pd.merge_asof(
            df,
            self.raw_data["Environment"],
            on="DateTime",
            by="DeviceId",
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

    def _get_nosepokes_datatable(self, visits_datatable: Datatable) -> Datatable:
        """
        Process raw nosepoke data into a structured Datatable.

        This method processes the raw 'Nosepokes' data from IntelliCage experiments,
        performing the following operations:
        - Replacing animal tags with animal IDs
        - Adding nosepoke duration information
        - Adding lick number and duration information
        - Adding water consumption estimation
        - Merging with visit data to associate nosepokes with visits
        - Creating a structured Datatable with defined variables and factors

        Parameters
        ----------
        visits_datatable : Datatable
            The processed visits datatable, used to associate nosepokes with visits.

        Returns
        -------
        Datatable
            A structured datatable containing processed nosepoke data.
        """
        df = self.raw_data["Nosepokes"].copy()
        visits_preprocessed_df = visits_datatable.original_df.copy()

        # Sanitize visits table before merging
        columns_to_drop = [
            "Timedelta",
            "Temperature",
            "Illumination",
        ]

        check_columns = ["LickNumber", "LickContactTime", "LickDuration"]
        for column in check_columns:
            if column in visits_preprocessed_df.columns:
                columns_to_drop.append(column)

        visits_preprocessed_df.drop(
            columns=columns_to_drop,
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
        df = pd.merge_asof(
            df,
            self.raw_data["Environment"],
            on="DateTime",
            by="DeviceId",
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
            "LicksContactTime": Variable(
                "LickContactTime",
                "sec",
                "Lick contact time",
                "float64",
                Aggregation.SUM,
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
            "LicksContactTime": Variable(
                "LicksContactTime",
                "sec",
                "Licks contact time",
                "float64",
                Aggregation.SUM,
                False,
            ),
        }

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

    def get_csv_data(
        self,
        export_registrations: bool,
        export_variables: bool,
    ) -> tuple[str, dict[str, pd.DataFrame]]:
        """
        Get CSV data for export.

        This method prepares data for export to CSV format. It can export both
        registration data (sessions) and variable data.

        Args:
            export_registrations (bool): Whether to export registration data.
            export_variables (bool): Whether to export variable data.

        Returns:
            tuple[str, dict[str, pd.DataFrame]]: A tuple containing the extension name and a dictionary
                mapping data types to DataFrames ready for CSV export.
        """
        result: dict[str, pd.DataFrame] = {}

        tag_to_animal_map = self.dataset.get_tag_to_name_map()

        if export_registrations:
            visits_data: dict[str, list | str] = {
                "DateTime": [],
                "DeviceType": EXTENSION_NAME,
                "DeviceId": [],
                "AnimalName": [],
                "AnimalTag": [],
                "TableType": "Visits",
                "ModuleName": [],
                "Start": [],
                "End": [],
                "Duration": [],
                "Corner": [],
                "CornerCondition": [],
                "PlaceError": [],
                "AntennaNumber": [],
                "AntennaDuration": [],
                "PresenceNumber": [],
                "PresenceDuration": [],
                "VisitSolution": [],
                "LickNumber": [],
                "LickContactTime": [],
                "LickDuration": [],
            }

            for row in self.raw_data["Visits"].itertuples():
                visits_data["DateTime"].append(row.Start)
                visits_data["DeviceId"].append(row.DeviceId)
                visits_data["AnimalName"].append(tag_to_animal_map[row.AnimalTag])
                visits_data["AnimalTag"].append(row.AnimalTag)

                visits_data["ModuleName"].append(row.ModuleName)
                visits_data["Start"].append(row.Start)
                visits_data["End"].append(row.End)
                visits_data["Duration"].append((row.End - row.Start).total_seconds())
                visits_data["Corner"].append(row.Corner)
                visits_data["CornerCondition"].append(row.CornerCondition)
                visits_data["PlaceError"].append(row.PlaceError)
                visits_data["AntennaNumber"].append(row.AntennaNumber)
                visits_data["AntennaDuration"].append(row.AntennaDuration)
                visits_data["PresenceNumber"].append(row.PresenceNumber)
                visits_data["PresenceDuration"].append(row.PresenceDuration)
                visits_data["VisitSolution"].append(row.VisitSolution)
                visits_data["LickNumber"].append(row.LickNumber)
                visits_data["LickContactTime"].append(row.LickContactTime)
                visits_data["LickDuration"].append(row.LickDuration)

            result["Visits"] = pd.DataFrame(visits_data)

        if export_variables:
            variables_csv_data = self.get_variables_csv_data(EXTENSION_NAME, tag_to_animal_map)
            result.update(variables_csv_data)

        return EXTENSION_NAME, result
