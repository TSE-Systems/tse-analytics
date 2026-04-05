import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Aggregation, Variable


def get_visits_datatable(dataset: Dataset) -> Datatable:
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
    df = dataset.raw_datatables["IntelliCage"]["Visits"].df.copy()

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
    if dataset.metadata["data_descriptor"]["Version"] == "Version1":
        df = pd.merge_asof(
            df,
            dataset.raw_datatables["IntelliCage"]["Environment"].df,
            on="DateTime",
            direction="nearest",
        )
    else:
        df = pd.merge_asof(
            df,
            dataset.raw_datatables["IntelliCage"]["Environment"].df,
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
    experiment_started = dataset.experiment_started
    df.insert(loc=3, column="Timedelta", value=df["DateTime"] - experiment_started)

    # Convert types
    df = df.astype({
        "Animal": "category",
        "PlaceError": "int64[pyarrow]",
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


def get_nosepokes_datatable(dataset: Dataset, visits_datatable: Datatable) -> Datatable:
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

    Returns
    -------
    Datatable
        A structured datatable containing processed nosepoke data.
    """
    df = dataset.raw_datatables["IntelliCage"]["Nosepokes"].df.copy()
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
    if dataset.metadata["data_descriptor"]["Version"] == "Version1":
        df = pd.merge_asof(
            df,
            dataset.raw_datatables["IntelliCage"]["Environment"].df,
            on="DateTime",
            direction="nearest",
        )
    else:
        df = pd.merge_asof(
            df,
            dataset.raw_datatables["IntelliCage"]["Environment"].df,
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

    if dataset.metadata["data_descriptor"]["Version"] != "Version1":
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
    experiment_started = dataset.experiment_started
    df.insert(loc=2, column="Timedelta", value=df["DateTime"] - experiment_started)

    # Add nosepoke-related columns to visits dataframe
    if dataset.metadata["data_descriptor"]["Version"] == "Version1":
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

    if dataset.metadata["data_descriptor"]["Version"] != "Version1":
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
        "SideError": "int64[pyarrow]",
        "TimeError": "int64[pyarrow]",
        "DoorState": "int64[pyarrow]",
        "AirState": "int64[pyarrow]",
        "ConditionError": "int64[pyarrow]",
    })

    # Convert to pyarrow backend
    df = df.convert_dtypes(dtype_backend="pyarrow")

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
