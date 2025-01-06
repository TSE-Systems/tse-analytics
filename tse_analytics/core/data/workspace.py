from uuid import UUID

from tse_analytics.core.data.dataset import Dataset


class Workspace:
    def __init__(self, name: str):
        self.name = name
        self.datasets: dict[UUID, Dataset] = {}
