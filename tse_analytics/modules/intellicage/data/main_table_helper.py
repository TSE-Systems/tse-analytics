import pandas as pd

from tse_analytics.modules.intellicage.data.ic_dataset import ICDataset


def preprocess_main_table(dataset: ICDataset, sampling_interval: pd.Timedelta) -> ICDataset:
    dataframes = []
    variables = {}
    if dataset.intelli_cage_data is not None:
        df_ag, variables_ag = dataset.intelli_cage_data.get_preprocessed_data()
        dataframes.append(df_ag)
        variables = variables | variables_ag

    # Sort variables by name
    variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

    df = pd.concat(dataframes, ignore_index=True, sort=False)

    animal_to_box_map = {}
    for animal in dataset.animals.values():
        animal_to_box_map[animal.id] = animal.box

    # Convert to categorical types
    df = df.astype({
        "Animal": "category",
    })

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    experiment_started = dataset.experiment_started
    experiment_stopped = dataset.experiment_stopped

    # Remove the time zone information and preserve local time
    df["DateTime"] = df["DateTime"].dt.tz_localize(None)

    datetime_range = pd.date_range(
        experiment_started.round("Min"), experiment_stopped.round("Min"), freq=sampling_interval
    )

    default_columns = [
        "DateTime",
        "Animal",
        "VisitID",
        "Cage",
        "Corner",
        "CornerCondition",
        "PlaceError",
        "LickNumber",
        "LickDuration",
        "ModuleName",
    ]
    agg = {}
    for column in df.columns:
        if column not in default_columns:
            if df.dtypes[column].name != "category":
                agg[column] = variables[column].aggregation
            else:
                agg[column] = "first"

    preprocessed_animal_df = []
    animal_ids = df["Animal"].unique().tolist()
    for i, animal_id in enumerate(animal_ids):
        animal_data = df[df["Animal"] == animal_id]
        preprocessed_df = _preprocess_animal(
            animal_id, animal_to_box_map[animal_id], animal_data, datetime_range, sampling_interval, agg
        )
        preprocessed_animal_df.append(preprocessed_df)

    df = pd.concat(preprocessed_animal_df, ignore_index=True, sort=False)

    # Add Run column
    df.insert(loc=5, column="Run", value=1)

    # Convert to categorical types
    df = df.astype({
        "Animal": "category",
    })

    df.sort_values(by=["Animal", "DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    dataset.original_df = df
    dataset.active_df = dataset.original_df.copy()
    dataset.sampling_interval = sampling_interval

    dataset.variables = variables

    # Remove absent animals
    animals = {}
    for animal in dataset.animals.values():
        if animal.id in animal_ids:
            animals[animal.id] = animal
    dataset.animals = animals

    return dataset


def _preprocess_animal(
    animal_id: str,
    box: int,
    df: pd.DataFrame,
    datetime_range: pd.DatetimeIndex,
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
    start_date_time = result.iloc[0]["DateTime"]
    result.insert(loc=1, column="Timedelta", value=result["DateTime"] - start_date_time)
    result.insert(loc=2, column="Bin", value=(result["Timedelta"] / sampling_interval).round().astype(int))

    # Put back animal into dataframe
    result.insert(loc=3, column="Animal", value=animal_id)

    # Put box numbers into dataframe
    result.insert(loc=4, column="Box", value=box)

    return result