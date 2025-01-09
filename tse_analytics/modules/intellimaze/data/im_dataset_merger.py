import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Animal, Variable
from tse_analytics.modules.intellimaze.data.im_dataset import IMDataset


def merge_datasets(
    new_dataset_name: str,
    datasets: list[Dataset],
    single_run: bool,
    continuous_mode: bool,
    generate_new_animal_names: bool,
) -> Dataset | None:
    if continuous_mode:
        return _merge_continuous(new_dataset_name, datasets, single_run)
    else:
        return _merge_overlap(new_dataset_name, datasets, single_run, generate_new_animal_names)


def _merge_continuous(new_dataset_name: str, datasets: list[Dataset], single_run: bool) -> Dataset | None:
    dfs = [x.original_df for x in datasets]

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
        "Animal": str,
    })

    new_df = new_df.astype({
        "Animal": "category",
    })

    new_animals = _merge_animals(datasets)
    new_variables = _merge_variables(datasets)
    new_meta = _merge_metadata(new_dataset_name, timedelta, new_animals, new_variables, datasets)

    result = IMDataset(
        name=new_dataset_name,
        path="",
        meta=new_meta,
        animals=new_animals,
        variables=new_variables,
        df=new_df,
        sampling_interval=timedelta,
    )
    return result


def _merge_overlap(
    new_dataset_name: str,
    datasets: list[Dataset],
    single_run: bool,
    generate_new_animal_names: bool,
) -> Dataset | None:
    if generate_new_animal_names:
        for index, dataset in enumerate(datasets):
            run_number = index + 1
            new_animals = {}
            name_map = {}
            for animal in dataset.animals.values():
                new_animal_id = f"{animal.id}_{run_number}"
                name_map[animal.id] = new_animal_id
                animal.id = new_animal_id
                new_animals[new_animal_id] = animal
            dataset.animals = new_animals
            dataset.original_df["Animal"] = dataset.original_df["Animal"].astype(str)
            dataset.original_df["Animal"] = dataset.original_df["Animal"].replace(name_map)
            dataset.original_df["Animal"] = dataset.original_df["Animal"].astype("category")

    dfs = [x.original_df for x in datasets]

    # reassign run number
    if not single_run:
        for index, df in enumerate(dfs):
            df["Run"] = index + 1

    new_df = pd.concat(dfs, ignore_index=True)

    if single_run:
        new_df["Run"] = 1

    # Drop DataTime column because of the overlap mode
    # new_df.drop(columns=["DateTime"], inplace=True)

    # find minimum sampling interval
    timedelta = min(dataset.sampling_interval for dataset in datasets)
    # new_df["Timedelta"] = new_df["DateTime"] - start_date_time
    new_df["Bin"] = (new_df["Timedelta"] / timedelta).round().astype(int)

    # convert categorical types
    new_df = new_df.astype({
        "Animal": str,
    })

    new_df = new_df.astype({
        "Animal": "category",
    })

    new_animals = _merge_animals(datasets)
    new_variables = _merge_variables(datasets)
    new_meta = _merge_metadata(new_dataset_name, timedelta, new_animals, new_variables, datasets)

    result = IMDataset(
        name=new_dataset_name,
        path="",
        meta=new_meta,
        animals=new_animals,
        variables=new_variables,
        df=new_df,
        sampling_interval=timedelta,
    )
    return result


def _merge_metadata(
    new_dataset_name: str,
    sampling_interval: pd.Timedelta,
    animals: dict[str, Animal],
    variables: dict[str, Variable],
    datasets: list[Dataset],
) -> dict:
    result = {
        "experiment": {
            "experiment_no": new_dataset_name,
        },
        "animals": {k: v.get_dict() for (k, v) in animals.items()},
        "tables": {
            "main_table": {
                "id": "main_table",
                "sample_interval": str(sampling_interval),
                "columns": {k: v.get_dict() for (k, v) in variables.items()},
            }
        },
        "origins": [dataset.meta for dataset in datasets],
    }
    return result


def _merge_animals(datasets: list[Dataset]) -> dict[str, Animal]:
    result: dict[str, Animal] = {}
    for animals in [dataset.animals for dataset in datasets]:
        result.update(animals)
    return result


def _merge_variables(datasets: list[Dataset]) -> dict[str, Variable]:
    result = datasets[0].variables
    return result
