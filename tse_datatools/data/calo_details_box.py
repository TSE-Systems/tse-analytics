from typing import Optional


class CaloDetailsBox:
    def __init__(
        self,
        box: int,
        ref_box: Optional[int],
    ):
        self.box = box
        self.ref_box = ref_box


def get_ref_box_number(box: int, boxes: list[int]) -> Optional[int]:
    assert len(boxes) > 0
    # find a gap between standard and reference boxes
    prev = boxes[-1]
    gap_index: Optional[int] = None
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
