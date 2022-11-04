from tse_datatools.data.dataset import Dataset


class Workspace:
    def __init__(self, name: str):
        self.name = name
        self.datasets: list[Dataset] = []
