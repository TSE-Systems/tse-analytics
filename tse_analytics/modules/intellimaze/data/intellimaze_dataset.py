from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.helper import rename_animal_df
from tse_analytics.core.data.shared import Animal
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.extension_tree_item import ExtensionTreeItem
from tse_analytics.modules.intellimaze.data.extension_data import ExtensionData


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

        self.extensions_data: dict[str, ExtensionData] = {}

    def get_tag_to_name_map(self) -> dict[str, str]:
        tag_to_animal_map = {}
        for animal in self.animals.values():
            tag_to_animal_map[animal.properties["Tag"]] = animal.id
        return tag_to_animal_map

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        super().rename_animal(old_id, animal)

        for extension_data in self.extensions_data.values():
            extension_data.raw_df = rename_animal_df(extension_data.raw_df, old_id, animal)

        messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def exclude_animals(self, animal_ids: set[str]) -> None:
        super().exclude_animals(animal_ids)

        for extension_data in self.extensions_data.values():
            extension_data.raw_df = extension_data.raw_df[~extension_data.raw_df["Animal"].isin(animal_ids)]

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        super().add_children_tree_items(dataset_tree_item)

        for extension_data in self.extensions_data.values():
            dataset_tree_item.add_child(ExtensionTreeItem(extension_data))
