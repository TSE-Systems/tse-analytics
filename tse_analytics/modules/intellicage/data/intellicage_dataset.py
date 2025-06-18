"""
IntelliCage Dataset Module.

This module provides the IntelliCageDataset class for representing and managing
complete IntelliCage experiment datasets, including animal data and experiment metadata.
"""

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Animal
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.extension_tree_item import ExtensionTreeItem
from tse_analytics.modules.intellicage.data.intellicage_data import IntelliCageData


class IntelliCageDataset(Dataset):
    """
    Class representing a complete IntelliCage experiment dataset.

    This class extends the base Dataset class to provide specific functionality
    for IntelliCage experiments, including handling of IntelliCage-specific data
    and visualization in the application's tree view.
    """

    def __init__(
        self,
        metadata: dict | list[dict],
        animals: dict[str, Animal],
    ):
        """
        Initialize the IntelliCageDataset object.

        Parameters
        ----------
        metadata : dict | list[dict]
            Metadata describing the experiment, including information about
            the experiment setup, conditions, and data descriptor.
        animals : dict[str, Animal]
            Dictionary mapping animal IDs to Animal objects containing
            information about each animal in the experiment.
        """
        super().__init__(
            metadata,
            animals,
        )

        self.intellicage_data: IntelliCageData | None = None

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        """
        Rename an animal in the dataset.

        This method updates the animal ID in the dataset and broadcasts a message
        to notify the application of the change.

        Parameters
        ----------
        old_id : str
            The current ID of the animal to be renamed.
        animal : Animal
            The Animal object with the new ID and properties.

        Returns
        -------
        None
        """
        super().rename_animal(old_id, animal)

        # if self.intellicage_data is not None:
        #     self.intellicage_data.raw_df = rename_animal_df(self.intellicage_data.raw_df, old_id, animal)

        messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def exclude_animals(self, animal_ids: set[str]) -> None:
        """
        Exclude specified animals from the dataset.

        This method removes data for the specified animals from the dataset,
        filtering out their entries from the raw data.

        Parameters
        ----------
        animal_ids : set[str]
            Set of animal IDs to exclude from the dataset.

        Returns
        -------
        None
        """
        super().exclude_animals(animal_ids)

        if self.intellicage_data is not None:
            self.intellicage_data.raw_df = self.intellicage_data.raw_df[
                ~self.intellicage_data.raw_df["Animal"].isin(animal_ids)
            ]

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        """
        Add IntelliCage-specific tree items to the dataset tree.

        This method adds visualization components for IntelliCage data to the
        application's tree view, allowing users to interact with the data.

        Parameters
        ----------
        dataset_tree_item : DatasetTreeItem
            The parent tree item to which IntelliCage-specific items will be added.

        Returns
        -------
        None
        """
        super().add_children_tree_items(dataset_tree_item)

        if self.intellicage_data is not None:
            dataset_tree_item.add_child(ExtensionTreeItem(self.intellicage_data))
