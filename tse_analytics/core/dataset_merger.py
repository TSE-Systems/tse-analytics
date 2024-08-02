import pandas as pd

from tse_analytics.modules.phenomaster.data.dataset import Dataset


def merge_datasets(
    new_dataset_name: str, datasets: list[Dataset], single_run: bool, continuous_mode: bool
) -> Dataset | None:
    if continuous_mode:
        return __merge_continuous(new_dataset_name, datasets, single_run)
    else:
        return __merge_overlap(new_dataset_name, datasets, single_run)


def __merge_continuous(new_dataset_name: str, datasets: list[Dataset], single_run: bool) -> Dataset | None:
    # sort datasets by start time
    datasets.sort(key=lambda x: x.start_timestamp)

    dfs = [x.original_df.copy() for x in datasets]

    # reassign run number
    if not single_run:
        for run, df in enumerate(dfs):
            df["Run"] = run + 1

    new_df = pd.concat(dfs, ignore_index=True)

    if single_run:
        new_df["Run"] = 1

    # reassign bin and timedelta
    start_date_time = new_df["DateTime"][0]
    # find minimum sampling interval
    timedelta = min(dataset.sampling_interval for dataset in datasets)
    new_df["Timedelta"] = new_df["DateTime"] - start_date_time
    new_df["Bin"] = (new_df["Timedelta"] / timedelta).round().astype(int)

    # convert categorical types
    new_df = new_df.astype({
        "Animal": "category",
        "Box": "category",
        "Bin": "category",
        "Run": "category",
    })

    new_path = ""
    new_meta = [dataset.meta for dataset in datasets]
    new_animals = {}
    for animals in [dataset.animals for dataset in datasets]:
        new_animals.update(animals)
    new_variables = datasets[0].variables
    new_sampling_interval = timedelta

    result = Dataset(
        name=new_dataset_name,
        path=new_path,
        meta=new_meta,
        animals=new_animals,
        variables=new_variables,
        df=new_df,
        sampling_interval=new_sampling_interval,
    )
    return result


def __merge_overlap(new_dataset_name: str, datasets: list[Dataset], single_run: bool) -> Dataset | None:
    # sort datasets by start time
    datasets.sort(key=lambda x: x.start_timestamp)

    dfs = [x.original_df.copy() for x in datasets]

    # reassign run number
    if not single_run:
        for run, df in enumerate(dfs):
            df["Run"] = run + 1

    new_df = pd.concat(dfs, ignore_index=True)

    if single_run:
        new_df["Run"] = 1

    # reassign bin and timedelta
    start_date_time = new_df["DateTime"][0]
    # find minimum sampling interval
    timedelta = min(dataset.sampling_interval for dataset in datasets)
    new_df["Timedelta"] = new_df["DateTime"] - start_date_time
    new_df["Bin"] = (new_df["Timedelta"] / timedelta).round().astype(int)

    # convert categorical types
    new_df = new_df.astype({
        "Animal": "category",
        "Box": "category",
        "Bin": "category",
        "Run": "category",
    })

    new_path = ""
    new_meta = [dataset.meta for dataset in datasets]
    new_animals = {}
    for animals in [dataset.animals for dataset in datasets]:
        new_animals.update(animals)
    new_variables = datasets[0].variables
    new_sampling_interval = timedelta

    result = Dataset(
        name=new_dataset_name,
        path=new_path,
        meta=new_meta,
        animals=new_animals,
        variables=new_variables,
        df=new_df,
        sampling_interval=new_sampling_interval,
    )
    return result
