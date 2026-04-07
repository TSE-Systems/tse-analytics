import pandas as pd
import pyarrow as pa

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable
from tse_analytics.globals import TIME_RESOLUTION_UNIT
from tse_analytics.modules.intellimaze.data.utils import get_tag_to_name_map, get_variables_csv_data

EXTENSION_NAME = "IntelliCage"


def preprocess_data(
    dataset: Dataset,
    extension_data: dict[str, Datatable],
) -> None:
    visits_datatable = _get_visits_datatable(dataset, extension_data)
    dataset.add_datatable(visits_datatable)

    nosepokes_datatable = _get_nosepokes_datatable(dataset, extension_data, visits_datatable)
    dataset.add_datatable(nosepokes_datatable)


def _get_visits_datatable(
    dataset: Dataset,
    extension_data: dict[str, Datatable],
) -> Datatable:
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
    df = extension_data["Visits"].df.copy()

    # Replace animal tags with animal IDs
    tag_to_animal_map = {}
    for animal in dataset.animals.values():
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
        extension_data["Environment"].df,
        on="DateTime",
        by="DeviceId",
        direction="nearest",
    )

    variables = {
        "VisitNumber": Variable(
            "VisitNumber",
            "count",
            "Visit number",
            "UInt64",
            Aggregation.SUM,
            False,
        ),
        "VisitDuration": Variable(
            "VisitDuration",
            "sec",
            "Visit duration",
            "Float64",
            Aggregation.SUM,
            False,
        ),
        "AntennaNumber": Variable(
            "AntennaNumber",
            "count",
            "Antenna number",
            "UInt64",
            Aggregation.SUM,
            False,
        ),
        "AntennaDuration": Variable(
            "AntennaDuration",
            "sec",
            "Antenna duration",
            "Float64",
            Aggregation.SUM,
            False,
        ),
        "PresenceNumber": Variable(
            "PresenceNumber",
            "count",
            "Presence number",
            "UInt64",
            Aggregation.SUM,
            False,
        ),
        "PresenceDuration": Variable(
            "PresenceDuration",
            "sec",
            "Presence duration",
            "Float64",
            Aggregation.SUM,
            False,
        ),
        "Temperature": Variable(
            "Temperature",
            "°C",
            "Cage temperature",
            "Float64",
            Aggregation.MEAN,
            False,
        ),
        "Illumination": Variable(
            "Illumination",
            "",
            "Cage illumination",
            "Float64",
            Aggregation.MEAN,
            False,
        ),
        "PlaceError": Variable(
            "PlaceError",
            "count",
            "Place error",
            "boolean",
            Aggregation.SUM,
            False,
        ),
    }

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Add Timedelta column
    experiment_started = dataset.experiment_started
    df.insert(
        loc=3,
        column="Timedelta",
        value=(df["DateTime"] - experiment_started).astype(pd.ArrowDtype(pa.duration(unit=TIME_RESOLUTION_UNIT))),
    )

    # Convert types
    df = df.astype({
        "Animal": "category",
        "PlaceError": "uint8[pyarrow]",
    })

    datatable = Datatable(
        dataset,
        "Visits",
        "IntelliCage visits data",
        variables,
        df,
        {
            "origin": "Visits",
        },
    )

    return datatable


def _get_nosepokes_datatable(
    dataset: Dataset,
    extension_data: dict[str, Datatable],
    visits_datatable: Datatable,
) -> Datatable:
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
    df = extension_data["Nosepokes"].df.copy()
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
    df = pd.merge_asof(
        df,
        extension_data["Environment"].df,
        on="DateTime",
        by="DeviceId",
        direction="nearest",
    )

    variables = {
        "NosepokeNumber": Variable(
            "NosepokeNumber",
            "count",
            "Nosepoke number",
            "UInt64",
            Aggregation.SUM,
            False,
        ),
        "NosepokeDuration": Variable(
            "NosepokeDuration",
            "sec",
            "Nosepoke duration",
            "Float64",
            Aggregation.MEAN,
            False,
        ),
        "PlaceError": Variable(
            "PlaceError",
            "count",
            "Place error",
            "boolean",
            Aggregation.SUM,
            False,
        ),
        "SideError": Variable(
            "SideError",
            "count",
            "Side error",
            "boolean",
            Aggregation.SUM,
            False,
        ),
        "TimeError": Variable(
            "TimeError",
            "count",
            "Time error",
            "boolean",
            Aggregation.SUM,
            False,
        ),
        "ConditionError": Variable(
            "ConditionError",
            "count",
            "Condition error",
            "boolean",
            Aggregation.SUM,
            False,
        ),
        "Temperature": Variable(
            "Temperature",
            "°C",
            "Cage temperature",
            "Float64",
            Aggregation.MEAN,
            False,
        ),
        "Illumination": Variable(
            "Illumination",
            "",
            "Cage illumination",
            "Float64",
            Aggregation.MEAN,
            False,
        ),
        "LickNumber": Variable(
            "LickNumber",
            "count",
            "Number of licks",
            "UInt64",
            Aggregation.SUM,
            False,
        ),
        "LickDuration": Variable(
            "LickDuration",
            "sec",
            "Licks duration",
            "Float64",
            Aggregation.SUM,
            False,
        ),
        "LicksContactTime": Variable(
            "LickContactTime",
            "sec",
            "Lick contact time",
            "Float64",
            Aggregation.SUM,
            False,
        ),
    }

    # Sort variables by name
    variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Add Timedelta column
    experiment_started = dataset.experiment_started
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
    visits_datatable.df = visits_datatable.df.join(grouped_by_visit, on="VisitID")

    visits_datatable.variables = visits_datatable.variables | {
        "NosepokesNumber": Variable(
            "NosepokesNumber",
            "count",
            "Number of nosepokes",
            "UInt64",
            Aggregation.SUM,
            False,
        ),
        "NosepokesDuration": Variable(
            "NosepokesDuration",
            "sec",
            "Duration of nosepokes",
            "Float64",
            Aggregation.SUM,
            False,
        ),
        "SideErrors": Variable(
            "SideErrors",
            "count",
            "Number of side errors",
            "UInt64",
            Aggregation.SUM,
            False,
        ),
        "TimeErrors": Variable(
            "TimeErrors",
            "count",
            "Number of time errors",
            "UInt64",
            Aggregation.SUM,
            False,
        ),
        "ConditionErrors": Variable(
            "ConditionErrors",
            "count",
            "Number of condition errors",
            "UInt64",
            Aggregation.SUM,
            False,
        ),
        "LicksNumber": Variable(
            "LicksNumber",
            "count",
            "Number of licks",
            "UInt64",
            Aggregation.SUM,
            False,
        ),
        "LicksDuration": Variable(
            "LicksDuration",
            "sec",
            "Licks duration",
            "Float64",
            Aggregation.SUM,
            False,
        ),
        "LicksContactTime": Variable(
            "LicksContactTime",
            "sec",
            "Licks contact time",
            "Float64",
            Aggregation.SUM,
            False,
        ),
    }

    # Sort visits variables by name
    visits_datatable.variables = dict(sorted(visits_datatable.variables.items(), key=lambda x: x[0].lower()))

    # Convert types
    df = df.astype({
        # "Animal": "category",
        "SideError": "uint8[pyarrow]",
        "TimeError": "uint8[pyarrow]",
        "DoorState": "uint8[pyarrow]",
        "AirState": "uint8[pyarrow]",
        "ConditionError": "uint8[pyarrow]",
    })

    datatable = Datatable(
        dataset,
        "Nosepokes",
        "IntelliCage nosepokes data",
        variables,
        df,
        {
            "origin": "Nosepokes",
        },
    )

    return datatable


def get_csv_data(
    dataset: Dataset,
    extension_data: dict[str, Datatable],
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

    tag_to_animal_map = get_tag_to_name_map(dataset.animals)

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

        for row in extension_data["Visits"].df.itertuples():
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
        variables_csv_data = get_variables_csv_data(extension_data, EXTENSION_NAME, tag_to_animal_map)
        result.update(variables_csv_data)

    return EXTENSION_NAME, result
