import pandas as pd

from tse_analytics.core.data.datatable import Datatable


class ExtensionData:
    def __init__(
        self,
        dataset: "IntelliMazeDataset",
        name: str,
        raw_data: dict[str, pd.DataFrame],
        device_ids: list[str],
    ):
        self.dataset = dataset
        self.name = name
        self.raw_data = raw_data
        self.device_ids = device_ids
        self.device_ids.sort()

    def get_raw_data(self):
        return self.raw_data

    def get_device_ids(self):
        return self.device_ids

    def preprocess_data(self) -> None:
        main_datatable = self.get_combined_datatable()
        self.dataset.add_datatable(main_datatable)

    def get_combined_datatable(self) -> Datatable:
        raise NotImplementedError("Subclasses must implement this method")
