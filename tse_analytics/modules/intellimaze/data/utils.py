import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.modules.intellimaze.data.extension_data import ExtensionData
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset


def get_combined_variables_table(extension_data: ExtensionData) -> pd.DataFrame:
    """
    Combine variable tables from different sources into a single DataFrame.

    This function processes integer, double, and boolean variable tables and combines them
    into a single DataFrame, sorted by datetime.

    Args:
        extension_data (ExtensionData): The extension data containing variable tables.

    Returns:
        pd.DataFrame: A combined DataFrame containing all variables.
    """
    result = pd.DataFrame()
    table_names = ["IntegerVariables", "DoubleVariables", "BooleanVariables"]
    for table_name in table_names:
        df = _preprocess_variable_table(table_name, extension_data)
        if df is not None:
            result = pd.concat([result, df], ignore_index=True, sort=False)
    result.sort_values(["DateTime"], inplace=True)
    result.reset_index(drop=True, inplace=True)

    # # Add Timedelta column
    # experiment_started = extension_data.dataset.experiment_started
    # result.insert(loc=1, column="Timedelta", value=result["DateTime"] - experiment_started)

    return result


def _preprocess_variable_table(table_name: str, extension_data: ExtensionData) -> pd.DataFrame | None:
    """
    Preprocess a variable table for use in analysis.

    This function performs several preprocessing steps:
    1. Replaces animal tags with animal IDs
    2. Renames columns for consistency
    3. Drops unnecessary columns
    4. Removes records without animal assignment
    5. Sorts by datetime
    6. Converts types
    7. Drops duplicate rows
    8. Pivots the data to create a wide-format table

    Args:
        table_name (str): The name of the table to preprocess.
        extension_data (ExtensionData): The extension data containing the table.

    Returns:
        pd.DataFrame | None: The preprocessed DataFrame, or None if the table doesn't exist.
    """
    if table_name not in extension_data.raw_data:
        return None

    df = extension_data.raw_data[table_name].copy()

    # Replace animal tags with animal IDs
    tag_to_animal_map = {}
    for animal in extension_data.dataset.animals.values():
        tag_to_animal_map[animal.properties["Tag"]] = animal.id
    df["Animal"] = df["Tag"].replace(tag_to_animal_map)

    # Rename columns
    df.rename(
        columns={
            "Time": "DateTime",
        },
        inplace=True,
    )

    # Drop the non-necessary columns
    df.drop(
        columns=[
            # "DeviceId",
            "Tag",
            "ConditionValue",
        ],
        inplace=True,
    )

    # Remove records without animal assignment
    df.dropna(subset=["Animal"], inplace=True)

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Convert types
    df = df.astype({
        "Animal": "category",
    })

    # Drop duplicate rows
    df.drop_duplicates(subset=["DateTime", "DeviceId"], keep="first", inplace=True, ignore_index=True)

    result = df.pivot(index=["DateTime", "Animal"], columns=["DeviceId", "Name"], values="Data").reset_index(drop=False)
    # result = df.pivot_table(values="Data", index=["DateTime", "Animal"], columns=["DeviceId", "Name"], aggfunc="first").reset_index(drop=False)

    # Drop the first column
    # result.drop(columns=result.columns[0], axis=1, inplace=True)

    # Rename MultiIndex columns
    result.columns = result.columns.map(lambda x: "".join(x) if x[1] == "" else "_".join(x))

    return result


def preprocess_main_table(dataset: IntelliMazeDataset) -> None:
    """
    Preprocess the main data table for an IntelliMazeDataset.

    This function combines data from all extensions into a single main table,
    performs type conversions, sorts the data, and adds the resulting datatable
    to the dataset.

    Args:
        dataset (IntelliMazeDataset): The dataset to preprocess.
    """
    datatables = []

    for extension_name in dataset.extensions_data.keys():
        datatables.append(dataset.datatables[extension_name])

    dataframes = []
    variables = {}
    for datatable in datatables:
        dataframes.append(datatable.active_df)
        variables = variables | datatable.variables

    # Sort variables by name
    variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

    df = pd.concat(dataframes, ignore_index=True, sort=False)

    # Convert types
    df = df.astype({
        "Animal": "category",
    })

    # Remove the time zone information and preserve local time
    # df["DateTime"] = df["DateTime"].dt.tz_localize(None)

    df.sort_values(["Timedelta"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    main_datatable = Datatable(
        dataset,
        "Main",
        "Main table",
        variables,
        df,
        None,
    )
    dataset.add_datatable(main_datatable)

    # animal_to_box_map = {}
    # for animal in dataset.animals.values():
    #     animal_to_box_map[animal.id] = animal.properties["PMBoxNr"]
    #
    # experiment_started = dataset.experiment_started
    # experiment_stopped = dataset.experiment_stopped
    #
    # datetime_range = pd.date_range(
    #     experiment_started.round("Min"), experiment_stopped.round("Min"), freq=sampling_interval
    # )
    #
    # default_columns = ["DateTime", "Animal"]
    # agg = {}
    # for column in df.columns:
    #     if column not in default_columns:
    #         if df.dtypes[column].name != "category":
    #             agg[column] = variables[column].aggregation
    #         else:
    #             agg[column] = "first"
    #
    # preprocessed_animal_df = []
    # animal_ids = df["Animal"].unique().tolist()
    # for i, animal_id in enumerate(animal_ids):
    #     animal_data = df[df["Animal"] == animal_id]
    #     preprocessed_df = _preprocess_animal(
    #         animal_id,
    #         animal_to_box_map[animal_id],
    #         animal_data,
    #         datetime_range,
    #         experiment_started,
    #         sampling_interval,
    #         agg,
    #     )
    #     preprocessed_animal_df.append(preprocessed_df)
    #
    # df = pd.concat(preprocessed_animal_df, ignore_index=True, sort=False)
    #
    # # Add Run column
    # df.insert(loc=5, column="Run", value=1)
    #
    # # Convert to categorical types
    # df = df.astype({
    #     "Animal": "category",
    # })
    #
    # df.sort_values(by=["DateTime", "Animal"], inplace=True)
    # df.reset_index(drop=True, inplace=True)
    #
    # dataset.original_df = df
    # dataset.active_df = dataset.original_df.copy()
    # dataset.sampling_interval = sampling_interval
    #
    # dataset.variables = variables
    #
    # # Remove absent animals
    # animals = {}
    # for animal in dataset.animals.values():
    #     if animal.id in animal_ids:
    #         animals[animal.id] = animal
    # dataset.animals = animals


def _preprocess_animal(
    animal_id: str,
    box: int,
    df: pd.DataFrame,
    datetime_range: pd.DatetimeIndex,
    experiment_started: pd.Timestamp,
    sampling_interval: pd.Timedelta,
    agg: dict[str, str],
) -> pd.DataFrame:
    """
    Preprocess data for a specific animal.

    This function performs several preprocessing steps:
    1. Decreases time resolution to minutes
    2. Resamples data with the specified interval
    3. Reindexes to the specified datetime range
    4. Fills missing data
    5. Adds Timedelta and Bin columns
    6. Adds Animal and Box columns

    Args:
        animal_id (str): The ID of the animal.
        box (int): The box number of the animal.
        df (pd.DataFrame): The DataFrame containing the animal's data.
        datetime_range (pd.DatetimeIndex): The datetime range to reindex to.
        experiment_started (pd.Timestamp): The timestamp when the experiment started.
        sampling_interval (pd.Timedelta): The sampling interval for resampling.
        agg (dict[str, str]): Dictionary mapping column names to aggregation functions.

    Returns:
        pd.DataFrame: The preprocessed DataFrame for the animal.
    """
    result = df.copy()

    # Decrease time resolution up to a minute
    result["DateTime"] = result["DateTime"].dt.round("Min")

    # Resample data with one minute interval
    result = result.resample(sampling_interval, on="DateTime", origin="start_day").aggregate(agg)

    result = result.reindex(datetime_range)
    # Fill missing data
    result.fillna(0, inplace=True)

    result.reset_index(drop=False, inplace=True, names=["DateTime"])

    # Add Timedelta and Bin columns
    result.insert(loc=1, column="Timedelta", value=result["DateTime"] - experiment_started)
    result.insert(loc=2, column="Bin", value=(result["Timedelta"] / sampling_interval).round().astype(int))

    # Put back animal into dataframe
    result.insert(loc=3, column="Animal", value=animal_id)

    # Put box numbers into dataframe
    result.insert(loc=4, column="Box", value=box)

    return result
