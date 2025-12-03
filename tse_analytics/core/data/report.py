from datetime import datetime
from uuid import uuid4


class Report:
    def __init__(
        self,
        dataset: "Dataset",
        name: str,
        content: str,
    ):
        self.id = uuid4()
        self.timestamp = datetime.now()

        self.dataset = dataset
        self.name = name
        self.content = content
