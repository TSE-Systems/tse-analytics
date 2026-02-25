"""
IntelliCage Data Processing Module.

This module provides the IntelliCageData class for processing raw IntelliCage data
into structured datatables for analysis.
"""

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable

if TYPE_CHECKING:
    from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset


class IntelliCageData:
    """
    Class for processing and managing IntelliCage experimental data.

    This class handles the raw data from IntelliCage experiments and processes it
    into structured datatables for visits and nosepokes, which can be used for
    further analysis.
    """

    def __init__(
        self,
        dataset: IntelliCageDataset,
        name: str,
        raw_data: dict[str, pd.DataFrame],
    ):
        """
        Initialize the IntelliCageData object.

        Parameters
        ----------
        dataset : IntelliCageDataset
            The parent dataset that this data belongs to.
        name : str
            The name of this data collection.
        raw_data : dict[str, pd.DataFrame]
            Dictionary containing raw data from IntelliCage experiments,
            with keys representing data types and values as pandas DataFrames.
        """
        self.dataset = dataset
        self.name = name
        self.raw_data = raw_data

        self.device_ids = self.raw_data["HardwareEvents"]["Cage"].unique().tolist()
        self.device_ids.sort()

    def get_raw_data(self):
        """
        Get the raw data dictionary.

        Returns
        -------
        dict[str, pd.DataFrame]
            Dictionary containing raw data from IntelliCage experiments.
        """
        return self.raw_data

    def get_device_ids(self):
        """
        Get the list of device IDs (cage identifiers) in the dataset.

        Returns
        -------
        list
            List of unique device IDs sorted in ascending order.
        """
        return self.device_ids

    def preprocess_data(self) -> None:
        """
        Process raw IntelliCage data into structured datatables.

        This method processes the raw data into two datatables:
        1. Visits datatable - containing information about animal visits to corners
        2. Nosepokes datatable - containing information about animal nosepokes

        Both datatables are added to the parent dataset for further analysis.

        Returns
        -------
        None
        """
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
        if self.dataset.metadata["data_descriptor"]["Version"] == "Version1":
            df = pd.merge_asof(
                df,
                self.raw_data["Environment"],
                on="DateTime",
                direction="nearest",
            )
        else:
            df = pd.merge_asof(
                df,
                self.raw_data["Environment"],
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
        visits_preprocessed_df = visits_datatable.df.copy()

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
        if self.dataset.metadata["data_descriptor"]["Version"] == "Version1":
            df = pd.merge_asof(
                df,
                self.raw_data["Environment"],
                on="DateTime",
                direction="nearest",
            )
        else:
            df = pd.merge_asof(
                df,
                self.raw_data["Environment"],
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
        visits_datatable.df = visits_datatable.df.join(grouped_by_visit, on="VisitID")

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
