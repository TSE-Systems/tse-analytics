from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from tse_analytics.core.data.dataset import Dataset


@dataclass
class Report:
    """
    Dataclass representing a report for a dataset.

    Attributes
    ----------
    dataset : Dataset
        The dataset this report belongs to.
    name : str
        The name of the report.
    content : str
        The content of the report.
    timestamp : datetime
        The timestamp when the report was created.
    """

    dataset: Dataset
    name: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
