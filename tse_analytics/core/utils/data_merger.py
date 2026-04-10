from dataclasses import asdict

import pandas as pd

from tse_analytics.core import color_manager
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Animal
from tse_analytics.globals import TIME_RESOLUTION_UNIT


def merge_datasets(
    new_dataset_name: str,
    datasets: list[Dataset],
    single_run: bool,
    continuous_mode: bool,
    generate_new_animal_names: bool,
) -> Dataset | None:
    """
    Merge multiple PhenoMaster datasets into a single dataset.

    This function serves as the main entry point for merging PhenoMaster datasets.
    It supports two merging modes: continuous (for sequential experiments) and
    overlap (for parallel experiments with potentially overlapping data).

    Args:
        new_dataset_name (str): Name for the merged dataset
        datasets (list[Dataset]): List of datasets to merge
        single_run (bool): If True, all data will be treated as a single experimental run
        continuous_mode (bool): If True, datasets are merged as sequential experiments;
                               if False, datasets are merged as parallel experiments
        generate_new_animal_names (bool): If True, animal IDs will be modified to ensure uniqueness
                                         across datasets (only used in overlap mode)

    Returns:
        Dataset | None: The merged dataset, or None if merging failed
    """
    # Sort datasets by experiment start time
    datasets.sort(key=lambda dataset: dataset.experiment_started)

    if not continuous_mode and generate_new_animal_names:
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
                datatable.df["Animal"] = datatable.df["Animal"].astype("string")
                datatable.df["Animal"] = datatable.df["Animal"].map(name_map)
                datatable.df["Animal"] = datatable.df["Animal"].astype("category")

            for extension_datatables in dataset.raw_datatables.values():
                for datatable in extension_datatables.values():
                    if "Animal" in datatable.df.columns:
                        datatable.df["Animal"] = datatable.df["Animal"].astype("string")
                        datatable.df["Animal"] = datatable.df["Animal"].map(name_map)
                        datatable.df["Animal"] = datatable.df["Animal"].astype("category")

    merged_animals = _merge_animals(datasets)
    for index, animal in enumerate(merged_animals.values()):
        animal.color = color_manager.get_color_hex(index)

    merging_mode = "continuous" if continuous_mode else "overlap"
    merged_metadata = _merge_metadata(new_dataset_name, merging_mode, merged_animals, datasets)

    merged_dataset = Dataset(
        new_dataset_name,
        "PhenoMaster merged dataset",
        "PhenoMaster",
        merged_metadata,
        merged_animals,
    )

    first_dataset = datasets[0]
    for datatable_name in first_dataset.datatables.keys():
        dataframes = []
        for dataset in datasets:
            if datatable_name in dataset.datatables:
                dataframes.append(dataset.datatables[datatable_name].df)

        # Assign run number
        if not single_run:
            for run, df in enumerate(dataframes):
                df["Run"] = run + 1

        new_df = pd.concat(dataframes, ignore_index=True)

        if single_run:
            if "Run" in new_df.columns:
                new_df = new_df.drop(columns=["Run"])
        else:
            new_df["Run"] = new_df["Run"].astype("UInt8")

        # Drop "Bin" column
        if "Bin" in new_df.columns:
            new_df = new_df.drop(columns=["Bin"])

        if continuous_mode:
            # Reassign timedelta column
            new_df["Timedelta"] = (new_df["DateTime"] - merged_dataset.experiment_started).dt.as_unit(
                TIME_RESOLUTION_UNIT
            )

        # Reset Animal category dtype
        new_df["Animal"] = new_df["Animal"].astype("string").astype("category")

        # Sort dataframe
        new_df = new_df.sort_values(by=["Timedelta", "Animal"]).reset_index(drop=True)

        new_variables = first_dataset.datatables[datatable_name].variables
        datatable = Datatable(
            merged_dataset,
            datatable_name,
            f"Merged {datatable_name} datatable",
            new_variables,
            new_df,
            {},
        )
        merged_dataset.add_datatable(datatable)

    _merge_raw_datatables(merged_dataset, datasets, continuous_mode)

    return merged_dataset


def _merge_raw_datatables(merged_dataset: Dataset, datasets: list[Dataset], continuous_mode: bool) -> None:
    """
    Merge raw_datatables (extension data) from source datasets into the merged dataset.

    Uses intersection semantics: only extensions and datatables present in every
    source dataset are merged. Before merging, assigns a `Timedelta` column (relative
    to each source dataset's experiment start) to every raw datatable so the merged
    result carries a consistent time-since-start column.

    Args:
        merged_dataset (Dataset): The destination merged dataset.
        datasets (list[Dataset]): Source datasets, sorted by start time.
    """

    first_dataset = datasets[0]
    for extension_name, extension_datatables in first_dataset.raw_datatables.items():
        # Intersection: extension must be present in every source dataset
        if not all(extension_name in ds.raw_datatables for ds in datasets):
            continue

        for datatable_name, reference_datatable in extension_datatables.items():
            # Intersection: datatable must be present in every source dataset's version
            if not all(datatable_name in ds.raw_datatables[extension_name] for ds in datasets):
                continue

            dataframes = [ds.raw_datatables[extension_name][datatable_name].df for ds in datasets]
            new_df = pd.concat(dataframes, ignore_index=True)

            if continuous_mode and "Timedelta" in new_df.columns:
                # Reassign timedelta column
                datetime_column = "StartDateTime" if "StartDateTime" in new_df.columns else "DateTime"
                new_df["Timedelta"] = (new_df[datetime_column] - merged_dataset.experiment_started).dt.as_unit(
                    TIME_RESOLUTION_UNIT
                )

            # Re-apply category dtype after concat (matches main-datatable handling)
            if "Animal" in new_df.columns:
                new_df["Animal"] = new_df["Animal"].astype("string").astype("category")

            # Sort by the appropriate time column
            if "Timedelta" in new_df.columns:
                sort_keys = ["Timedelta"] + (["Animal"] if "Animal" in new_df.columns else [])
                new_df = new_df.sort_values(by=sort_keys).reset_index(drop=True)
            elif "StartDateTime" in new_df.columns:
                sort_keys = ["StartDateTime"] + (["Animal"] if "Animal" in new_df.columns else [])
                new_df = new_df.sort_values(by=sort_keys).reset_index(drop=True)
            elif "DateTime" in new_df.columns:
                sort_keys = ["DateTime"] + (["Animal"] if "Animal" in new_df.columns else [])
                new_df = new_df.sort_values(by=sort_keys).reset_index(drop=True)

            # Copy metadata from the reference version, drop the stale origin_path
            new_metadata = {k: v for k, v in reference_datatable.metadata.items() if k != "origin_path"}

            # Recompute animal_ids if present (e.g. GroupHousing) so it reflects the merged data
            if "animal_ids" in new_metadata and "Animal" in new_df.columns:
                animal_ids = new_df["Animal"].dropna().unique().tolist()
                animal_ids.sort()
                new_metadata["animal_ids"] = animal_ids

            datatable = Datatable(
                merged_dataset,
                datatable_name,
                f"Merged {datatable_name} datatable",
                reference_datatable.variables,
                new_df,
                new_metadata,
            )
            merged_dataset.add_raw_datatable(extension_name, datatable)


def _merge_metadata(
    merged_dataset_name: str,
    merging_mode: str,
    merged_animals: dict[str, Animal],
    datasets: list[Dataset],
) -> dict:
    """
    Merge metadata from multiple datasets.

    This helper function creates a new metadata dictionary for the merged dataset,
    combining information from all source datasets. It determines the experiment
    start and end times based on the merging mode.

    Args:
        merged_dataset_name (str): Name for the merged dataset
        merging_mode (str): The mode used for merging ("continuous" or "overlap")
        merged_animals (dict[str, Animal]): Dictionary of merged animal objects
        datasets (list[Dataset]): List of datasets being merged

    Returns:
        dict: Merged metadata dictionary
    """
    experiment_started = datasets[0].experiment_started
    if merging_mode == "continuous":
        experiment_stopped = datasets[-1].experiment_stopped
    else:
        experiment_stopped = max(dataset.experiment_stopped for dataset in datasets)

    result = {
        "merging_mode": merging_mode,
        "experiment_started": str(experiment_started),
        "experiment_stopped": str(experiment_stopped),
        "animals": {k: asdict(v) for (k, v) in merged_animals.items()},
        "runs": {},
    }
    for i, dataset in enumerate(datasets):
        result["runs"][str(i + 1)] = dataset.metadata
    return result


def _merge_animals(datasets: list[Dataset]) -> dict[str, Animal]:
    """
    Merge animal data from multiple datasets.

    This helper function combines animal data from all datasets into a single dictionary.
    When animals with the same ID exist in multiple datasets, the animal from the later
    dataset (in the input list) takes precedence. The resulting dictionary is sorted by
    animal ID.

    Args:
        datasets (list[Dataset]): List of datasets whose animal data will be merged

    Returns:
        dict[str, Animal]: Dictionary mapping animal IDs to Animal objects
    """
    result: dict[str, Animal] = {}
    for animals in [dataset.animals for dataset in reversed(datasets)]:
        result.update(animals)
    result = dict(sorted(result.items()))
    return result
