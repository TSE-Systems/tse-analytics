from enum import unique, Enum
from typing import Optional

import pandas as pd

from tse_datatools.data.dataset import Dataset


@unique
class MergingMode(Enum):
    CONCATENATE = "Concatenate"
    OVERLAP = "Overlap"


def merge_datasets(new_dataset_name: str, datasets: list[Dataset], merging_mode: MergingMode) -> Optional[Dataset]:
    if len(datasets) < 2:
        raise Exception("At least two datasets should be selected")

    # sort datasets by start time
    datasets.sort(key=lambda x: x.start_timestamp)

    dfs = [x.original_df for x in datasets]
    new_df = None
    if merging_mode is MergingMode.CONCATENATE:
        new_df = pd.concat(dfs, ignore_index=True)

    new_path = ""
    new_meta = datasets[0].meta
    new_boxes = datasets[0].boxes
    new_animals = datasets[0].animals
    new_variables = datasets[0].variables
    new_sampling_interval = datasets[0].sampling_interval

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
