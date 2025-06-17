import pandas as pd

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.modules.intellimaze.data.extension_data import ExtensionData
from tse_analytics.modules.intellimaze.data.intellimaze_dataset import IntelliMazeDataset


def get_combined_variables_table(extension_data: ExtensionData) -> pd.DataFrame:
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
