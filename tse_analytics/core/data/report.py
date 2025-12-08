from datetime import datetime


class Report:
    def __init__(
        self,
        dataset: "Dataset",
        name: str,
        content: str,
    ):
        self.timestamp = datetime.now()

        self.dataset = dataset
        self.name = name
        self.content = content
