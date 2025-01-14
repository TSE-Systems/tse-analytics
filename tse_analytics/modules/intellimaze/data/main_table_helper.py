import pandas as pd

from tse_analytics.modules.intellimaze.data.im_dataset import IMDataset


def preprocess_main_table(dataset: IMDataset, sampling_interval: pd.Timedelta) -> IMDataset:
    dataframes = []
    variables = {}
    if dataset.animal_gate_data is not None:
        df_ag, variables_ag = dataset.animal_gate_data.get_preprocessed_data()
        dataframes.append(df_ag)
        variables = variables | variables_ag

    if dataset.running_wheel_data is not None:
        df_rw, variables_rw = dataset.running_wheel_data.get_preprocessed_data()
        dataframes.append(df_rw)
        variables = variables | variables_rw

    if dataset.consumption_scale_data is not None:
        df_cs, variables_cs = dataset.consumption_scale_data.get_preprocessed_data()
        dataframes.append(df_cs)
        variables = variables | variables_cs

    # Sort variables by name
    variables = dict(sorted(variables.items(), key=lambda x: x[0].lower()))

    df = pd.concat(dataframes, ignore_index=True, sort=False)

    animal_to_box_map = {}
    for animal in dataset.animals.values():
        animal_to_box_map[animal.id] = animal.box

    # Put box numbers into dataframe
    df["Box"] = df["Animal"]
    df["Box"] = df["Box"].replace(animal_to_box_map)

    # Convert to categorical types
    df = df.astype({
        "Animal": "category",
    })

    df.sort_values(["DateTime"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Add Timedelta and Bin columns
    start_date_time = df.iloc[0]["DateTime"]
    df.insert(loc=1, column="Timedelta", value=df["DateTime"] - start_date_time)
    df.insert(loc=2, column="Bin", value=(df["Timedelta"] / sampling_interval).round().astype(int))

    # Add Run column
    df.insert(loc=5, column="Run", value=1)

    dataset.original_df = df
    dataset.active_df = dataset.original_df.copy()
    dataset.sampling_interval = sampling_interval

    dataset.variables = variables

    experiment_started = dataset.experiment_started
    experiment_stopped = dataset.experiment_stopped

    return dataset
