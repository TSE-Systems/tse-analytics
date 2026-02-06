from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tse_analytics.core.data.dataset import Dataset


class Report:
    def __init__(
        self,
        dataset: Dataset,
        name: str,
        content: str,
    ):
        self.timestamp = datetime.now()

        self.dataset = dataset
        self.name = name
        self.content = content
