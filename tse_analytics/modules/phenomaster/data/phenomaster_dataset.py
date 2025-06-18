import numpy as np

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
    """
    Dataset class for PhenoMaster experimental data.

    This class extends the base Dataset class to handle specific data types and operations
    related to PhenoMaster experiments. It manages data from different PhenoMaster modules
    including calorimetry, drinking/feeding, activity monitoring, and traffic cage.

    Attributes:
        calo_data (CaloData | None): Calorimetry data containing metabolic measurements
        drinkfeed_data (DrinkFeedData | None): Drinking and feeding data
        actimot_data (ActimotData | None): Activity and motion tracking data
        trafficage_data (TraffiCageData | None): Traffic cage movement data
    """

    def __init__(
        self,
        metadata: dict | list[dict],
        animals: dict[str, Animal],
    ):
        """
        Initialize a PhenoMasterDataset.

        Args:
            metadata (dict | list[dict]): Metadata describing the dataset
            animals (dict[str, Animal]): Dictionary mapping animal IDs to Animal objects
        """
        super().__init__(
            metadata,
            animals,
        )

        self.calo_data: CaloData | None = None
        self.drinkfeed_data: DrinkFeedData | None = None
        self.actimot_data: ActimotData | None = None
        self.trafficage_data: TraffiCageData | None = None

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        """
        Rename an animal in the dataset.

        This method overrides the base class method to handle PhenoMaster-specific
        data structures. It updates the animal ID in all relevant data components
        and broadcasts a dataset changed message.

        Args:
            old_id (str): The current ID of the animal to be renamed
            animal (Animal): The Animal object with the new ID and properties
        """
        super().rename_animal(old_id, animal)

        # if self.drinkfeed_data is not None:
        #     self.drinkfeed_data.raw_df = rename_animal_df(self.drinkfeed_data.raw_df, old_id, animal)
        # if self.calo_data is not None:
        #     self.calo_data.raw_df = rename_animal_df(self.calo_data.raw_df, old_id, animal)
        # if self.actimot_data is not None:
        #     self.actimot_data.raw_df = self._rename_animal_df(self.actimot_data.raw_df, old_id, animal)

        messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def exclude_animals(self, animal_ids: set[str]) -> None:
        """
        Exclude specified animals from the dataset.

        This method overrides the base class method to handle PhenoMaster-specific
        data structures. It removes data for the specified animals from all
        PhenoMaster data components (calo, drinkfeed, actimot).

        Args:
            animal_ids (set[str]): Set of animal IDs to exclude from the dataset
        """
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
        """
        Append calorimetry fitting results to the dataset.

        This method adds predicted values from calorimetry fitting results to the main
        datatable. It creates new variables for predicted values if they don't exist,
        and updates the dataset with the fitting results.

        Args:
            fitting_results (dict[int, CaloFittingResult]): Dictionary mapping box numbers
                to calorimetry fitting results
        """
        if len(fitting_results) > 0:
            main_datatable = self.datatables["Main"]
            active_df = main_datatable.original_df
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

            if "O2-p" not in main_datatable.variables:
                main_datatable.variables["O2-p"] = Variable(
                    "O2-p", "[%]", "Predicted O2", "float64", Aggregation.MEAN, False
                )
            if "CO2-p" not in main_datatable.variables:
                main_datatable.variables["CO2-p"] = Variable(
                    "CO2-p", "[%]", "Predicted CO2", "float64", Aggregation.MEAN, False
                )
            if "VO2(3)-p" not in main_datatable.variables:
                main_datatable.variables["VO2(3)-p"] = Variable(
                    "VO2(3)-p", "[ml/h]", "Predicted VO2(3)", "float64", Aggregation.MEAN, False
                )
            if "VCO2(3)-p" not in main_datatable.variables:
                main_datatable.variables["VCO2(3)-p"] = Variable(
                    "VCO2(3)-p", "[ml/h]", "Predicted VCO2(3)", "float64", Aggregation.MEAN, False
                )
            if "RER-p" not in main_datatable.variables:
                main_datatable.variables["RER-p"] = Variable(
                    "RER-p", "", "Predicted RER", "float64", Aggregation.MEAN, False
                )
            if "H(3)-p" not in main_datatable.variables:
                main_datatable.variables["H(3)-p"] = Variable(
                    "H(3)-p", "[kcal/h]", "Predicted H(3)", "float64", Aggregation.MEAN, False
                )
            main_datatable.refresh_active_df()
            messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        """
        Add PhenoMaster-specific child items to the dataset tree.

        This method overrides the base class method to add tree items for each
        PhenoMaster data component (drinkfeed, actimot, calo, trafficage) if they exist.
        These tree items allow for navigation and visualization of the different
        data components in the UI.

        Args:
            dataset_tree_item (DatasetTreeItem): The parent dataset tree item to add children to
        """
        super().add_children_tree_items(dataset_tree_item)

        if self.drinkfeed_data is not None:
            dataset_tree_item.add_child(DrinkFeedTreeItem(self.drinkfeed_data))

        if self.actimot_data is not None:
            dataset_tree_item.add_child(ActimotTreeItem(self.actimot_data))

        if self.calo_data is not None:
            dataset_tree_item.add_child(CaloDataTreeItem(self.calo_data))

        if self.trafficage_data is not None:
            dataset_tree_item.add_child(TraffiCageTreeItem(self.trafficage_data))
