from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Animal


class IntelliMazeDataset(Dataset):
    """
    Dataset class for IntelliMaze experiments.

    This class extends the base Dataset class to provide functionality specific to IntelliMaze datasets.
    It manages device information and extension data for various IntelliMaze components.
    """

    def __init__(
        self,
        name: str,
        description: str,
        metadata: dict | list[dict],
        animals: dict[str, Animal],
    ):
        """
        Initialize an IntelliMazeDataset.

        Args:
            name (str): Name of the dataset.
            description (str): Description of the dataset.
            metadata (dict | list[dict]): Metadata for the dataset.
            animals (dict[str, Animal]): Dictionary mapping animal IDs to Animal objects.
        """
        super().__init__(
            name,
            description,
            metadata,
            animals,
        )

    @property
    def devices(self) -> dict[str, list[str]]:
        """
        Dictionary mapping extension names to lists of device IDs
        """
        return self.metadata.get("devices", {})

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

        messaging.broadcast(messaging.DatasetChangedMessage(self, self))
