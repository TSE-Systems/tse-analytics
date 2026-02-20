"""
Module containing the Dataset class for managing experimental data.

This module provides functionality for handling datasets, including metadata, animals,
factors, and datatables. It supports operations like renaming animals, excluding time ranges,
and applying binning and outlier detection.
"""

from copy import deepcopy
from datetime import datetime
from uuid import uuid4

import pandas as pd

from tse_analytics.core import messaging
from tse_analytics.core.color_manager import get_factor_level_color_hex
from tse_analytics.core.data.binning import BinningSettings
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.outliers import OutliersMode, OutliersSettings
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import Animal, Factor, FactorLevel
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.datatable_tree_item import DatatableTreeItem
from tse_analytics.core.models.report_tree_item import ReportTreeItem
from tse_analytics.core.models.tree_item import TreeItem


class Dataset:
    """
    A class representing an experimental dataset.

    The Dataset class manages experimental data, including metadata, animals, factors,
    and datatables. It provides methods for manipulating the dataset, such as renaming
    animals, excluding time ranges, and applying binning and outlier detection.
    """

    def __init__(
        self,
        metadata: dict | list[dict],
        animals: dict[str, Animal],
    ):
        """
        Initialize a Dataset instance.

        Parameters
        ----------
        metadata : dict or list[dict]
            Metadata describing the dataset, including name, description, and experiment times.
        animals : dict[str, Animal]
            Dictionary mapping animal IDs to Animal objects.
        """
        self.id = uuid4()
        self.metadata = metadata

        self.animals = animals
        self.factors: dict[str, Factor] = {}
        self.datatables: dict[str, Datatable] = {}

        self.outliers_settings = OutliersSettings(OutliersMode.OFF, 1.5)
        self.binning_settings = BinningSettings()

        self.reports: dict[str, Report] = {}

    @property
    def name(self) -> str:
        """
        Get the name of the dataset.

        Returns
        -------
        str
            The name of the dataset from metadata.
        """
        return self.metadata["name"]

    @property
    def description(self) -> str:
        """
        Get the description of the dataset.

        Returns
        -------
        str
            The description of the dataset from metadata.
        """
        return self.metadata["description"]

    @property
    def source_path(self) -> str:
        """
        Get the source path of the dataset.

        Returns
        -------
        str
            The source path of the dataset from metadata, or an empty string if not available.
        """
        return self.metadata["source_path"] if "source_path" in self.metadata else ""

    @property
    def experiment_started(self) -> pd.Timestamp:
        """
        Get the start time of the experiment.

        Returns
        -------
        pd.Timestamp
            The start time of the experiment as a pandas Timestamp.
        """
        return pd.to_datetime(self.metadata["experiment_started"], utc=False).tz_localize(None)

    @property
    def experiment_stopped(self) -> pd.Timestamp:
        """
        Get the end time of the experiment.

        Returns
        -------
        pd.Timestamp
            The end time of the experiment as a pandas Timestamp.
        """
        return pd.to_datetime(self.metadata["experiment_stopped"], utc=False).tz_localize(None)

    @property
    def experiment_duration(self) -> pd.Timedelta:
        """
        Get the duration of the experiment.

        Returns
        -------
        pd.Timedelta
            The duration of the experiment as a pandas Timedelta.
        """
        return self.experiment_stopped - self.experiment_started

    def add_datatable(self, datatable: Datatable) -> None:
        """
        Add a datatable to the dataset.

        Parameters
        ----------
        datatable : Datatable
            The datatable to add to the dataset.
        """
        self.datatables[datatable.name] = datatable

    def remove_datatable(self, datatable: Datatable) -> None:
        """
        Remove a datatable from the dataset.

        Parameters
        ----------
        datatable : Datatable
            The datatable to remove from the dataset.
        """
        self.datatables.pop(datatable.name)

    def rename(self, name: str) -> None:
        """
        Rename the dataset.

        Parameters
        ----------
        name : str
            The new name for the dataset.
        """
        self.metadata["name"] = name

    def extract_levels_from_property(self, property_name: str) -> dict[str, FactorLevel]:
        """
        Extract factor levels from an animal property.

        This method creates factor levels based on the values of a specific property
        across all animals in the dataset.

        Parameters
        ----------
        property_name : str
            The name of the animal property to extract levels from.

        Returns
        -------
        dict[str, FactorLevel]
            A dictionary mapping level names to FactorLevel objects.
        """
        levels_dict: dict[str, list[str]] = {}
        levels: dict[str, FactorLevel] = {}
        for animal in self.animals.values():
            if property_name not in animal.properties:
                return levels
            level_name = str(animal.properties[property_name])
            if level_name not in levels_dict:
                levels_dict[level_name] = []
            levels_dict[level_name].append(animal.id)

        index = 0
        for key, value in levels_dict.items():
            level = FactorLevel(
                name=key,
                color=get_factor_level_color_hex(index),
                animal_ids=value,
            )
            levels[level.name] = level
            index += 1

        # Sort levels by name
        levels = dict(sorted(levels.items(), key=lambda x: x[0].lower()))
        return levels

    def rename_animal(self, old_id: str, animal: Animal) -> None:
        """
        Rename an animal in the dataset.

        This method updates the animal ID in all datatables, factors, and metadata.

        Parameters
        ----------
        old_id : str
            The current ID of the animal.
        animal : Animal
            The animal object with the new ID.
        """
        for datatable in self.datatables.values():
            datatable.rename_animal(old_id, animal)

        # Rename animal in factor's levels definitions
        for factor in self.factors.values():
            for level in factor.levels:
                for i, animal_id in enumerate(level.animal_ids):
                    if animal_id == old_id:
                        level.animal_ids[i] = animal.id

        # Rename animal in metadata
        new_dict = {}
        for item in self.metadata["animals"].values():
            if item["id"] == old_id:
                item["id"] = animal.id
            new_dict[item["id"]] = item
        self.metadata["animals"] = new_dict

        # Rename animal in dictionary
        self.animals.pop(old_id)
        self.animals[animal.id] = animal

        # messaging.broadcast(messaging.DatasetChangedMessage(self, self))

    def exclude_animals(self, animal_ids: set[str]) -> None:
        """
        Exclude animals from the dataset.

        This method removes the specified animals from the dataset, including
        from factors, metadata, and datatables.

        Parameters
        ----------
        animal_ids : set[str]
            Set of animal IDs to exclude from the dataset.
        """
        # Remove animals from factor's levels definitions
        for factor in self.factors.values():
            for level in factor.levels:
                level_set = set(level.animal_ids)
                filtered_set = level_set.difference(animal_ids)
                level.animal_ids = list(filtered_set)

        for animal_id in animal_ids:
            self.animals.pop(animal_id)

        if "animals" in self.metadata:
            new_meta_animals = {}
            for item in self.metadata["animals"].values():
                if item["id"] not in animal_ids:
                    new_meta_animals[item["id"]] = item
            self.metadata["animals"] = new_meta_animals

        for datatable in self.datatables.values():
            datatable.exclude_animals(animal_ids)

    def exclude_time(self, range_start: datetime, range_end: datetime) -> None:
        """
        Exclude a time range from the dataset.

        This method removes data within the specified time range from the dataset,
        adjusting experiment start and end times if necessary.

        Parameters
        ----------
        range_start : datetime
            Start of the time range to exclude.
        range_end : datetime
            End of the time range to exclude.
        """
        if range_start <= self.experiment_started < range_end:
            self.metadata["experiment_started"] = str(range_end)
        if range_start < self.experiment_stopped <= range_end:
            self.metadata["experiment_stopped"] = str(range_start)
        for datatable in self.datatables.values():
            datatable.exclude_time(range_start, range_end)

    def trim_time(self, range_start: datetime, range_end: datetime) -> None:
        """
        Trim the dataset to a specific time range.

        This method keeps only data within the specified time range,
        updating experiment start and end times accordingly.

        Parameters
        ----------
        range_start : datetime
            New start time for the dataset.
        range_end : datetime
            New end time for the dataset.
        """
        self.metadata["experiment_started"] = str(range_start)
        self.metadata["experiment_stopped"] = str(range_end)
        for datatable in self.datatables.values():
            datatable.trim_time(range_start, range_end)

    def resample(self, resampling_interval: pd.Timedelta) -> None:
        """
        Resample all datatables in the dataset.

        This method applies the specified resampling interval to all datatables
        in the dataset.

        Parameters
        ----------
        resampling_interval : pd.Timedelta
            The time interval to resample the data to.
        """
        for datatable in self.datatables.values():
            datatable.resample(resampling_interval)

    def set_factors(self, factors: dict[str, Factor]) -> None:
        """
        Set the factors for the dataset.

        This method updates the factors in the dataset and applies them to all datatables.

        Parameters
        ----------
        factors : dict[str, Factor]
            Dictionary mapping factor names to Factor objects.
        """
        self.factors = factors

        for datatable in self.datatables.values():
            datatable.set_factors(factors)

    def apply_binning(self, binning_settings: BinningSettings) -> None:
        """
        Apply binning settings to the dataset.

        This method updates the binning settings for the dataset and broadcasts
        a message to notify listeners of the change.

        Parameters
        ----------
        binning_settings : BinningSettings
            The binning settings to apply to the dataset.
        """
        self.binning_settings = binning_settings
        messaging.broadcast(messaging.BinningMessage(self, self, binning_settings))

    def apply_outliers(self, settings: OutliersSettings) -> None:
        """
        Apply outlier detection settings to the dataset.

        This method updates the outlier detection settings for the dataset and
        broadcasts a message to notify listeners of the change.

        Parameters
        ----------
        settings : OutliersSettings
            The outlier detection settings to apply to the dataset.
        """
        self.outliers_settings = settings
        messaging.broadcast(messaging.DataChangedMessage(self, self))

    def clone(self):
        """
        Create a deep copy of the dataset.

        Returns
        -------
        Dataset
            A new Dataset instance that is a deep copy of this dataset.
        """
        return deepcopy(self)

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None:
        """
        Add datatables as children to a dataset tree item.

        This method is used for building a tree representation of the dataset
        and its datatables.

        Parameters
        ----------
        dataset_tree_item : DatasetTreeItem
            The dataset tree item to add children to.
        """
        dataset_tree_item.clear()
        for datatable in self.datatables.values():
            dataset_tree_item.add_child(DatatableTreeItem(datatable))

        # Add reports nodes
        if len(self.reports) > 0:
            reports_node = TreeItem("Reports")
            dataset_tree_item.add_child(reports_node)
            for report in self.reports.values():
                reports_node.add_child(ReportTreeItem(report))

    def add_report(self, report: Report) -> None:
        if report.name in self.reports:
            self.reports[report.name].content += report.content
        else:
            self.reports[report.name] = report

    def delete_report(self, name: str) -> None:
        self.reports.pop(name)

    def __setstate__(self, state):
        """
        Restore the state of the dataset during unpickling.

        This method is called when unpickling a Dataset object. It updates the
        object's state and refreshes the active dataframes in all datatables.

        Parameters
        ----------
        state : dict
            The state dictionary to restore from.
        """
        self.__dict__.update(state)
        for datatable in self.datatables.values():
            # Recalculate active_df dataframes
            datatable.refresh_active_df()

        # TODO: remove the check in the future
        if "reports" not in self.__dict__:
            self.reports = {}
