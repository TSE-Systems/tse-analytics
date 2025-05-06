from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.helper import rename_animal_df
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
        metadata: dict | list[dict],
        animals: dict[str, Animal],
        devices: dict[str, list[str]],
    ):
        super().__init__(
            metadata,
            animals,
        )

        self.devices = devices

        self.animal_gate_data: AnimalGateData | None = None
        self.running_wheel_data: RunningWheelData | None = None
        self.consumption_scale_data: ConsumptionScaleData | None = None

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        super().rename_animal(old_id, animal)

        if self.animal_gate_data is not None:
            self.animal_gate_data.raw_df = rename_animal_df(self.animal_gate_data.raw_df, old_id, animal)

        if self.running_wheel_data is not None:
            self.running_wheel_data.raw_df = rename_animal_df(self.running_wheel_data.raw_df, old_id, animal)

        if self.consumption_scale_data is not None:
            self.consumption_scale_data.raw_df = rename_animal_df(self.consumption_scale_data.raw_df, old_id, animal)

        messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def exclude_animals(self, animal_ids: set[str]) -> None:
        super().exclude_animals(animal_ids)

        if self.animal_gate_data is not None:
            self.animal_gate_data.raw_df = self.animal_gate_data.raw_df[
                ~self.animal_gate_data.raw_df["Animal"].isin(animal_ids)
            ]

        if self.running_wheel_data is not None:
            self.running_wheel_data.raw_df = self.running_wheel_data.raw_df[
                ~self.running_wheel_data.raw_df["Animal"].isin(animal_ids)
            ]

        if self.consumption_scale_data is not None:
            self.consumption_scale_data.raw_df = self.consumption_scale_data.raw_df[
                ~self.consumption_scale_data.raw_df["Animal"].isin(animal_ids)
            ]

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        super().add_children_tree_items(dataset_tree_item)

        if self.animal_gate_data is not None:
            dataset_tree_item.add_child(ExtensionTreeItem(self.animal_gate_data))

        if self.running_wheel_data is not None:
            dataset_tree_item.add_child(ExtensionTreeItem(self.running_wheel_data))

        if self.consumption_scale_data is not None:
            dataset_tree_item.add_child(ExtensionTreeItem(self.consumption_scale_data))
