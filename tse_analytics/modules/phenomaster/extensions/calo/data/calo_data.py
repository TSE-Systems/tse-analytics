from typing import TYPE_CHECKING

import pandas as pd

from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.data.phenomaster_extension_data import PhenoMasterExtensionData

if TYPE_CHECKING:
    from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


def _get_ref_box_number(box: int, boxes: list[int]) -> int | None:
    assert len(boxes) > 0
    # find a gap between standard and reference boxes
    prev = boxes[-1]
    gap_index: int | None = None
    for idx, this in reversed(list(enumerate(boxes))):
        if this < prev - 1:
            gap_index = idx
            break
        prev = this

    if gap_index is None:
        return None

    ref_boxes = boxes[gap_index + 1 :]
    if box in ref_boxes:
        return None

    standard_boxes = boxes[: gap_index + 1]

    parts = len(standard_boxes) // len(ref_boxes)

    box_index = standard_boxes.index(box)
    ref_box_index = box_index // parts
    return ref_boxes[ref_box_index]


class CaloData(PhenoMasterExtensionData):
    def __init__(
        self,
        dataset: PhenoMasterDataset,
        name: str,
        path: str,
        variables: dict[str, Variable],
        raw_df: pd.DataFrame,
        sampling_interval: pd.Timedelta,
    ):
        super().__init__(
            dataset,
            name,
            raw_df,
            variables,
            meta={
                "origin_path": path,
                "sampling_interval": sampling_interval,
            },
        )

        # Assign reference calo boxes
        all_box_numbers = raw_df["Box"].unique().tolist()
        self.ref_box_mapping: dict[int, int] = {}
        for box in all_box_numbers:
            self.ref_box_mapping[box] = _get_ref_box_number(box, all_box_numbers)
