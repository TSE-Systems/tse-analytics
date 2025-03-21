import pandas as pd

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Animal
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


def merge_datasets(
    new_dataset_name: str,
    datasets: list[PhenoMasterDataset],
    single_run: bool,
    continuous_mode: bool,
    generate_new_animal_names: bool,
) -> PhenoMasterDataset | None:
    # sort datasets by start time
    datasets.sort(key=lambda dataset: dataset.experiment_started)

    if continuous_mode:
        merged_dataset = _merge_continuous(new_dataset_name, datasets, single_run)
    else:
        merged_dataset = _merge_overlap(new_dataset_name, datasets, single_run, generate_new_animal_names)

    for index, animal in enumerate(merged_dataset.animals.values()):
        animal.color = color_manager.get_color_hex(index)

    return merged_dataset


def _merge_continuous(
    merged_dataset_name: str,
    datasets: list[PhenoMasterDataset],
    single_run: bool,
) -> PhenoMasterDataset | None:
    first_dataset = datasets[0]

    merged_animals = _merge_animals(datasets)
    merged_metadata = _merge_metadata(merged_dataset_name, "continuous", merged_animals, datasets)

    result = PhenoMasterDataset(
        name=merged_dataset_name,
        description="PhenoMaster dataset merged in continuous mode.",
        path="",
        meta=merged_metadata,
        animals=merged_animals,
    )

    for datatable_name in first_dataset.datatables.keys():
        dataframes = []
        for datasets in datasets:
            dataframes.append(datasets.datatables[datatable_name].original_df)

        # reassign run number
        if not single_run:
            for run, df in enumerate(dataframes):
                df["Run"] = run + 1

        new_df = pd.concat(dataframes, ignore_index=True)

        if single_run:
            new_df["Run"] = 1

        # Drop "Bin" column
        new_df.drop(columns=["Bin"], inplace=True)

        # reassign bin and timedelta
        start_date_time = new_df["DateTime"][0]
        new_df["Timedelta"] = new_df["DateTime"] - start_date_time

        # convert categorical types
        new_df = new_df.astype({
            "Animal": str,
        })
        new_df = new_df.astype({
            "Animal": "category",
            "Run": int,
        })

        # Sort dataframe
        # new_df.sort_values(by=["Timedelta", "Animal"], inplace=True)
        # new_df.reset_index(drop=True, inplace=True)

        new_variables = first_dataset.datatables[datatable_name].variables
        datatable = Datatable(
            result,
            datatable_name,
            f"Merged {datatable_name} datatable",
            new_variables,
            new_df,
            None,
        )
        result.add_datatable(datatable)

    return result


def _merge_overlap(
    merged_dataset_name: str,
    datasets: list[PhenoMasterDataset],
    single_run: bool,
    generate_new_animal_names: bool,
) -> PhenoMasterDataset | None:
    first_dataset = datasets[0]

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

            for datatable in dataset.datatables.values():
                datatable.original_df["Animal"] = datatable.original_df["Animal"].astype(str)
                datatable.original_df["Animal"] = datatable.original_df["Animal"].replace(name_map)
                datatable.original_df["Animal"] = datatable.original_df["Animal"].astype("category")

    merged_animals = _merge_animals(datasets)
    merged_metadata = _merge_metadata(merged_dataset_name, "overlap", merged_animals, datasets)

    result = PhenoMasterDataset(
        name=merged_dataset_name,
        description="PhenoMaster dataset merged in overlap mode.",
        path="",
        meta=merged_metadata,
        animals=merged_animals,
    )

    for datatable_name in first_dataset.datatables.keys():
        dataframes = []
        for datasets in datasets:
            dataframes.append(datasets.datatables[datatable_name].original_df)

        # reassign run number
        if not single_run:
            for index, df in enumerate(dataframes):
                df["Run"] = index + 1

        new_df = pd.concat(dataframes, ignore_index=True)

        if single_run:
            new_df["Run"] = 1

        # Drop "Bin" column
        new_df.drop(columns=["Bin"], inplace=True)

        # convert categorical types
        new_df = new_df.astype({
            "Animal": str,
        })
        new_df = new_df.astype({
            "Animal": "category",
            "Run": int,
        })

        # Sort dataframe
        new_df.sort_values(by=["Timedelta", "Animal"], inplace=True)
        new_df.reset_index(drop=True, inplace=True)

        new_variables = first_dataset.datatables[datatable_name].variables
        datatable = Datatable(
            result,
            datatable_name,
            f"Merged {datatable_name} datatable",
            new_variables,
            new_df,
            None,
        )
        result.add_datatable(datatable)

    return result


def _merge_metadata(
    merged_dataset_name: str,
    merging_mode: str,
    merged_animals: dict[str, Animal],
    datasets: list[PhenoMasterDataset],
) -> dict:
    result = {
        "experiment": {
            "experiment_no": merged_dataset_name,
            "merging_mode": merging_mode,
        },
        "animals": {k: v.get_dict() for (k, v) in merged_animals.items()},
        "runs": {},
    }
    for i, dataset in enumerate(datasets):
        result["runs"][str(i + 1)] = dataset.metadata
    return result


def _merge_animals(datasets: list[PhenoMasterDataset]) -> dict[str, Animal]:
    result: dict[str, Animal] = {}
    for animals in [dataset.animals for dataset in reversed(datasets)]:
        result.update(animals)
    result = dict(sorted(result.items()))
    return result
