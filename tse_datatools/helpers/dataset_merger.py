from enum import unique, Enum
from typing import Optional

import pandas as pd
from PySide6.QtWidgets import QMessageBox, QWidget

from tse_datatools.data.dataset import Dataset


@unique
class MergingMode(Enum):
    CONCATENATE = "Concatenate"
    OVERLAP = "Overlap"


def merge_datasets(
    new_dataset_name: str, datasets: list[Dataset], merging_mode: MergingMode, parent_widget: QWidget
) -> Optional[Dataset]:
    # check number of datasets
    if len(datasets) < 2:
        QMessageBox.critical(
            parent_widget,
            "Cannot merge datasets!",
            "At least two datasets should be selected.",
            buttons=QMessageBox.StandardButton.Abort,
            defaultButton=QMessageBox.StandardButton.Abort,
        )
        return None

    # check variables compatibility
    first_variables_set = datasets[0].variables
    for dataset in datasets:
        if dataset.variables != first_variables_set:
            QMessageBox.critical(
                parent_widget,
                "Cannot merge datasets!",
                "List of variables should be the same.",
                buttons=QMessageBox.StandardButton.Abort,
                defaultButton=QMessageBox.StandardButton.Abort,
            )
            return None

    # sort datasets by start time
    datasets.sort(key=lambda x: x.start_timestamp)

    dfs = [x.original_df.copy() for x in datasets]

    # reassign run number
    for run, df in enumerate(dfs):
        df["Run"] = run + 1

    new_df = None
    if merging_mode is MergingMode.CONCATENATE:
        new_df = pd.concat(dfs, ignore_index=True)

    # reassign bin and timedelta
    start_date_time = new_df["DateTime"][0]
    # find minimum sampling interval
    timedelta = min([dataset.sampling_interval for dataset in datasets])
    new_df["Timedelta"] = new_df["DateTime"] - start_date_time
    new_df["Bin"] = (new_df["Timedelta"] / timedelta).round().astype(int)

    # convert categorical types
    new_df = new_df.astype(
        {
            "Animal": "category",
            "Box": "category",
            "Bin": "category",
            "Run": "category",
        }
    )

    new_path = ""
    new_meta = [dataset.meta for dataset in datasets]
    new_boxes = {}
    for box in [dataset.boxes for dataset in datasets]:
        new_boxes.update(box)
    new_animals = {}
    for animals in [dataset.animals for dataset in datasets]:
        new_animals.update(animals)
    new_variables = datasets[0].variables
    new_sampling_interval = timedelta

    result = Dataset(
        name=new_dataset_name,
        path=new_path,
        meta=new_meta,
        boxes=new_boxes,
        animals=new_animals,
        variables=new_variables,
        df=new_df,
        sampling_interval=new_sampling_interval,
    )
    return result
