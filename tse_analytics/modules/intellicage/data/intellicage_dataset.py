import pandas as pd

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.helper import rename_animal_df
from tse_analytics.core.data.shared import Animal
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.extension_tree_item import ExtensionTreeItem
from tse_analytics.modules.intellicage.data.intellicage_data import IntelliCageData


class IntelliCageDataset(Dataset):
    def __init__(
        self,
        name: str,
        description: str,
        path: str,
        metadata: dict | list[dict],
        animals: dict[str, Animal],
    ):
        super().__init__(
            name,
            description,
            path,
            metadata,
            animals,
        )

        self.experiment_started = pd.to_datetime(
            self.metadata["experiment"]["Interval"]["Start"], utc=False
        ).tz_localize(None)
        self.experiment_stopped = pd.to_datetime(self.metadata["experiment"]["Interval"]["End"], utc=False).tz_localize(
            None
        )

        self.intellicage_data: IntelliCageData | None = None

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        super().rename_animal(old_id, animal)

        # if self.intellicage_data is not None:
        #     self.intellicage_data.raw_df = rename_animal_df(self.intellicage_data.raw_df, old_id, animal)

        messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def exclude_animals(self, animal_ids: set[str]) -> None:
        super().exclude_animals(animal_ids)

        if self.intellicage_data is not None:
            self.intellicage_data.raw_df = self.intellicage_data.raw_df[
                ~self.intellicage_data.raw_df["Animal"].isin(animal_ids)
            ]

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        super().add_children_tree_items(dataset_tree_item)

        if self.intellicage_data is not None:
            dataset_tree_item.add_child(ExtensionTreeItem(self.intellicage_data))
