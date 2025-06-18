from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.helper import rename_animal_df
from tse_analytics.core.data.shared import Animal
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.extension_tree_item import ExtensionTreeItem
from tse_analytics.modules.intellimaze.data.extension_data import ExtensionData


class IntelliMazeDataset(Dataset):
    """
    Dataset class for IntelliMaze experiments.

    This class extends the base Dataset class to provide functionality specific to IntelliMaze datasets.
    It manages device information and extension data for various IntelliMaze components.

    Attributes:
        devices (dict[str, list[str]]): Dictionary mapping extension names to lists of device IDs.
        extensions_data (dict[str, ExtensionData]): Dictionary mapping extension names to their data.
    """
    def __init__(
        self,
        metadata: dict | list[dict],
        animals: dict[str, Animal],
        devices: dict[str, list[str]],
    ):
        """
        Initialize an IntelliMazeDataset.

        Args:
            metadata (dict | list[dict]): Metadata for the dataset.
            animals (dict[str, Animal]): Dictionary mapping animal IDs to Animal objects.
            devices (dict[str, list[str]]): Dictionary mapping extension names to lists of device IDs.
        """
        super().__init__(
            metadata,
            animals,
        )

        self.devices = devices

        self.extensions_data: dict[str, ExtensionData] = {}

    def get_tag_to_name_map(self) -> dict[str, str]:
        """
        Get a mapping from animal tags to animal IDs.

        Returns:
            dict[str, str]: Dictionary mapping animal tags to animal IDs.
        """
        tag_to_animal_map = {}
        for animal in self.animals.values():
            tag_to_animal_map[animal.properties["Tag"]] = animal.id
        return tag_to_animal_map

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        """
        Rename an animal in the dataset and update all related data.

        This method updates the animal ID in all extension data and broadcasts a dataset changed message.

        Args:
            old_id (str): The old animal ID.
            animal (Animal): The animal object with the new ID.
        """
        super().rename_animal(old_id, animal)

        for extension_data in self.extensions_data.values():
            extension_data.raw_df = rename_animal_df(extension_data.raw_df, old_id, animal)

        messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def exclude_animals(self, animal_ids: set[str]) -> None:
        """
        Exclude animals from the dataset.

        This method removes data for the specified animals from all extension data.

        Args:
            animal_ids (set[str]): Set of animal IDs to exclude.
        """
        super().exclude_animals(animal_ids)

        for extension_data in self.extensions_data.values():
            extension_data.raw_df = extension_data.raw_df[~extension_data.raw_df["Animal"].isin(animal_ids)]

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        """
        Add child tree items for extensions to the dataset tree item.

        Args:
            dataset_tree_item (DatasetTreeItem): The dataset tree item to add children to.
        """
        super().add_children_tree_items(dataset_tree_item)

        for extension_data in self.extensions_data.values():
            dataset_tree_item.add_child(ExtensionTreeItem(extension_data))
