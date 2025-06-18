"""
IntelliCage Dataset Merger Module.

This module provides functions for merging multiple IntelliCage datasets into a single dataset.
It supports different merging strategies, including continuous mode (datasets are treated as
sequential in time) and overlap mode (datasets are treated as parallel experiments).
"""

import pandas as pd

from tse_analytics.core import color_manager
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Animal
from tse_analytics.modules.intellicage.data.intellicage_dataset import IntelliCageDataset


def merge_datasets(
    new_dataset_name: str,
    datasets: list[IntelliCageDataset],
    single_run: bool,
    continuous_mode: bool,
    generate_new_animal_names: bool,
) -> IntelliCageDataset | None:
    """
    Merge multiple IntelliCage datasets into a single dataset.

    This function serves as the main entry point for merging IntelliCage datasets.
    It supports two merging strategies:
    1. Continuous mode: Datasets are treated as sequential in time
    2. Overlap mode: Datasets are treated as parallel experiments

    Parameters
    ----------
    new_dataset_name : str
        Name for the merged dataset.
    datasets : list[IntelliCageDataset]
        List of IntelliCageDataset objects to merge.
    single_run : bool
        If True, all data will be treated as a single experimental run.
        If False, run numbers will be assigned based on the source dataset.
    continuous_mode : bool
        If True, datasets will be merged in continuous mode (sequential in time).
        If False, datasets will be merged in overlap mode (parallel experiments).
    generate_new_animal_names : bool
        If True, new animal names will be generated to avoid conflicts.
        Only applies in overlap mode.

    Returns
    -------
    IntelliCageDataset | None
        The merged dataset, or None if the merge failed.
    """
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
    datasets: list[IntelliCageDataset],
    single_run: bool,
) -> IntelliCageDataset | None:
    """
    Merge datasets in continuous mode (sequential in time).

    This function merges multiple IntelliCage datasets treating them as sequential
    in time. It concatenates the data from all datasets, adjusting timedeltas and
    run numbers as needed.

    Parameters
    ----------
    merged_dataset_name : str
        Name for the merged dataset.
    datasets : list[IntelliCageDataset]
        List of IntelliCageDataset objects to merge, sorted by start time.
    single_run : bool
        If True, all data will be treated as a single experimental run.
        If False, run numbers will be assigned based on the source dataset.

    Returns
    -------
    IntelliCageDataset | None
        The merged dataset, or None if the merge failed.
    """
    first_dataset = datasets[0]

    merged_animals = _merge_animals(datasets)
    merged_metadata = _merge_metadata(merged_dataset_name, "continuous", merged_animals, datasets)

    result = IntelliCageDataset(
        metadata=merged_metadata,
        animals=merged_animals,
    )

    for datatable_name in first_dataset.datatables.keys():
        dataframes = []
        for dataset in datasets:
            dataframes.append(dataset.datatables[datatable_name].original_df)

        # reassign run number
        if not single_run:
            for run, df in enumerate(dataframes):
                df["Run"] = run + 1

        new_df = pd.concat(dataframes, ignore_index=True)

        if single_run:
            new_df["Run"] = 1

        # reassign bin and timedelta
        start_date_time = result.experiment_started
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
    datasets: list[IntelliCageDataset],
    single_run: bool,
    generate_new_animal_names: bool,
) -> IntelliCageDataset | None:
    """
    Merge datasets in overlap mode (parallel experiments).

    This function merges multiple IntelliCage datasets treating them as parallel
    experiments. It can optionally generate new animal names to avoid conflicts
    between datasets.

    Parameters
    ----------
    merged_dataset_name : str
        Name for the merged dataset.
    datasets : list[IntelliCageDataset]
        List of IntelliCageDataset objects to merge, sorted by start time.
    single_run : bool
        If True, all data will be treated as a single experimental run.
        If False, run numbers will be assigned based on the source dataset.
    generate_new_animal_names : bool
        If True, new animal names will be generated to avoid conflicts by
        appending the run number to the original animal ID.

    Returns
    -------
    IntelliCageDataset | None
        The merged dataset, or None if the merge failed.
    """
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

    result = IntelliCageDataset(
        metadata=merged_metadata,
        animals=merged_animals,
    )

    for datatable_name in first_dataset.datatables.keys():
        dataframes = []
        for dataset in datasets:
            dataframes.append(dataset.datatables[datatable_name].original_df)

        # reassign run number
        if not single_run:
            for index, df in enumerate(dataframes):
                df["Run"] = index + 1

        new_df = pd.concat(dataframes, ignore_index=True)

        if single_run:
            new_df["Run"] = 1

        # convert categorical types
        new_df = new_df.astype({
            "Animal": str,
        })
        new_df = new_df.astype({
            "Animal": "category",
            "Run": int,
        })

        # TODO: reassign bin and timedelta. HOW?
        # start_date_time = result.experiment_started
        # new_df["Timedelta"] = new_df["DateTime"] - start_date_time

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
    datasets: list[IntelliCageDataset],
) -> dict:
    """
    Merge metadata from multiple datasets.

    This function creates a new metadata dictionary for the merged dataset,
    combining information from all source datasets.

    Parameters
    ----------
    merged_dataset_name : str
        Name for the merged dataset.
    merging_mode : str
        The mode used for merging ("continuous" or "overlap").
    merged_animals : dict[str, Animal]
        Dictionary of animals in the merged dataset.
    datasets : list[IntelliCageDataset]
        List of source datasets.

    Returns
    -------
    dict
        Merged metadata dictionary.
    """
    experiment_started = datasets[0].experiment_started
    if merging_mode == "continuous":
        experiment_stopped = datasets[len(datasets) - 1].experiment_stopped
    else:
        experiment_stopped = max(dataset.experiment_stopped for dataset in datasets)

    result = {
        "name": merged_dataset_name,
        "description": "IntelliCage dataset",
        "merging_mode": merging_mode,
        "experiment_started": str(experiment_started),
        "experiment_stopped": str(experiment_stopped),
        "animals": {k: v.get_dict() for (k, v) in merged_animals.items()},
        "runs": {},
    }
    for i, dataset in enumerate(datasets):
        result["runs"][str(i + 1)] = dataset.metadata
    return result


def _merge_animals(datasets: list[IntelliCageDataset]) -> dict[str, Animal]:
    """
    Merge animals from multiple datasets.

    This function creates a new dictionary of animals by combining animals
    from all source datasets. If the same animal ID appears in multiple datasets,
    the animal from the first dataset is used.

    Parameters
    ----------
    datasets : list[IntelliCageDataset]
        List of source datasets.

    Returns
    -------
    dict[str, Animal]
        Dictionary mapping animal IDs to Animal objects for the merged dataset.
    """
    result: dict[str, Animal] = {}
    for animals in [dataset.animals for dataset in reversed(datasets)]:
        result.update(animals)
    result = dict(sorted(result.items()))
    return result
