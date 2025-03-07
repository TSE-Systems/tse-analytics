import pandas as pd

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Animal
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.extension_tree_item import ExtensionTreeItem
from tse_analytics.modules.intellimaze.submodules.animal_gate.data.animal_gate_data import AnimalGateData
from tse_analytics.modules.intellimaze.submodules.consumption_scale.data.consumption_scale_data import (
    ConsumptionScaleData,
)
from tse_analytics.modules.intellimaze.submodules.running_wheel.data.running_wheel_data import RunningWheelData


class IntelliMazeDataset(Dataset):
    def __init__(
        self,
        name: str,
        path: str,
        meta: dict | list[dict],
        devices: dict[str, list[str]],
        animals: dict[str, Animal],
    ):
        super().__init__(
            name,
            path,
            meta,
            animals,
            {},
            pd.DataFrame(),
            None,
        )

        self.devices = devices

        self.animal_gate_data: AnimalGateData | None = None
        self.running_wheel_data: RunningWheelData | None = None
        self.consumption_scale_data: ConsumptionScaleData | None = None

    @property
    def experiment_started(self) -> pd.Timestamp:
        return pd.to_datetime(self.meta["experiment"]["ExperimentStarted"], format="%m/%d/%Y %H:%M:%S")

    @property
    def experiment_stopped(self) -> pd.Timestamp:
        return pd.to_datetime(self.meta["experiment"]["ExperimentStopped"], format="%m/%d/%Y %H:%M:%S")

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        if self.animal_gate_data is not None:
            dataset_tree_item.add_child(ExtensionTreeItem(self.animal_gate_data))

        if self.running_wheel_data is not None:
            dataset_tree_item.add_child(ExtensionTreeItem(self.running_wheel_data))

        if self.consumption_scale_data is not None:
            dataset_tree_item.add_child(ExtensionTreeItem(self.consumption_scale_data))
