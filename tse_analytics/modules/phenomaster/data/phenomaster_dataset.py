import numpy as np
import pandas as pd

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Aggregation, Animal, Variable
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.modules.phenomaster.submodules.actimot.data.actimot_data import ActimotData
from tse_analytics.modules.phenomaster.submodules.actimot.models.actimot_tree_item import ActimotTreeItem
from tse_analytics.modules.phenomaster.submodules.calo.calo_fitting_result import CaloFittingResult
from tse_analytics.modules.phenomaster.submodules.calo.data.calo_data import CaloData
from tse_analytics.modules.phenomaster.submodules.calo.models.calo_tree_item import CaloDataTreeItem
from tse_analytics.modules.phenomaster.submodules.drinkfeed.data.drinkfeed_data import DrinkFeedData
from tse_analytics.modules.phenomaster.submodules.drinkfeed.models.drinkfeed_tree_item import DrinkFeedTreeItem
from tse_analytics.modules.phenomaster.submodules.trafficage.data.trafficage_data import TraffiCageData
from tse_analytics.modules.phenomaster.submodules.trafficage.models.trafficage_tree_item import TraffiCageTreeItem


class PhenoMasterDataset(Dataset):
    def __init__(
        self,
        name: str,
        path: str,
        meta: dict | list[dict],
        animals: dict[str, Animal],
        variables: dict[str, Variable],
        df: pd.DataFrame,
        sampling_interval: pd.Timedelta,
    ):
        super().__init__(
            name,
            path,
            meta,
            animals,
            variables,
            df,
            sampling_interval,
        )

        self.calo_data: CaloData | None = None
        self.drinkfeed_data: DrinkFeedData | None = None
        self.actimot_data: ActimotData | None = None
        self.trafficage_data: TraffiCageData | None = None

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        super().rename_animal(old_id, animal)

        if self.drinkfeed_data is not None:
            self.drinkfeed_data.raw_df = self._rename_animal_df(self.drinkfeed_data.raw_df, old_id, animal)
        if self.calo_data is not None:
            self.calo_data.raw_df = self._rename_animal_df(self.calo_data.raw_df, old_id, animal)
        if self.actimot_data is not None:
            self.actimot_data.raw_df = self._rename_animal_df(self.actimot_data.raw_df, old_id, animal)

        messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def exclude_animals(self, animal_ids: set[str]) -> None:
        super().exclude_animals(animal_ids)

        if self.calo_data is not None:
            self.calo_data.raw_df = self.calo_data.raw_df[~self.calo_data.raw_df["Animal"].isin(animal_ids)]
        if self.drinkfeed_data is not None:
            self.drinkfeed_data.raw_df = self.drinkfeed_data.raw_df[
                ~self.drinkfeed_data.raw_df["Animal"].isin(animal_ids)
            ]
        if self.actimot_data is not None:
            self.actimot_data.raw_df = self.actimot_data.raw_df[~self.actimot_data.raw_df["Animal"].isin(animal_ids)]

    def append_fitting_results(
        self,
        fitting_results: dict[int, CaloFittingResult],
    ) -> None:
        if len(fitting_results) > 0:
            active_df = self.original_df
            active_df["O2-p"] = np.nan
            active_df["CO2-p"] = np.nan
            active_df["VO2(3)-p"] = np.nan
            active_df["VCO2(3)-p"] = np.nan
            active_df["RER-p"] = np.nan
            active_df["H(3)-p"] = np.nan
            for result in fitting_results.values():
                for _index, row in result.df.iterrows():
                    bin_number = row["Bin"]

                    # TODO: TODO: check int -> str conversion for general table!
                    active_df.loc[
                        active_df[(active_df["Box"] == result.box_number) & (active_df["Bin"] == bin_number)].index[0],
                        ["O2-p", "CO2-p", "VO2(3)-p", "VCO2(3)-p", "RER-p", "H(3)-p"],
                    ] = [row["O2-p"], row["CO2-p"], row["VO2(3)-p"], row["VCO2(3)-p"], row["RER-p"], row["H(3)-p"]]

            if "O2-p" not in self.variables:
                self.variables["O2-p"] = Variable("O2-p", "[%]", "Predicted O2", "float64", Aggregation.MEAN, False)
            if "CO2-p" not in self.variables:
                self.variables["CO2-p"] = Variable("CO2-p", "[%]", "Predicted CO2", "float64", Aggregation.MEAN, False)
            if "VO2(3)-p" not in self.variables:
                self.variables["VO2(3)-p"] = Variable(
                    "VO2(3)-p", "[ml/h]", "Predicted VO2(3)", "float64", Aggregation.MEAN, False
                )
            if "VCO2(3)-p" not in self.variables:
                self.variables["VCO2(3)-p"] = Variable(
                    "VCO2(3)-p", "[ml/h]", "Predicted VCO2(3)", "float64", Aggregation.MEAN, False
                )
            if "RER-p" not in self.variables:
                self.variables["RER-p"] = Variable("RER-p", "", "Predicted RER", "float64", Aggregation.MEAN, False)
            if "H(3)-p" not in self.variables:
                self.variables["H(3)-p"] = Variable(
                    "H(3)-p", "[kcal/h]", "Predicted H(3)", "float64", Aggregation.MEAN, False
                )
            self.refresh_active_df()
            messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        if self.drinkfeed_data is not None:
            dataset_tree_item.add_child(DrinkFeedTreeItem(self.drinkfeed_data))

        if self.actimot_data is not None:
            dataset_tree_item.add_child(ActimotTreeItem(self.actimot_data))

        if self.calo_data is not None:
            dataset_tree_item.add_child(CaloDataTreeItem(self.calo_data))

        if self.trafficage_data is not None:
            dataset_tree_item.add_child(TraffiCageTreeItem(self.trafficage_data))
