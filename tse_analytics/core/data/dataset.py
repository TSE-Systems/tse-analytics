"""
Module containing the Dataset class for managing experimental data.

This module provides functionality for handling datasets, including metadata, animals,
factors, and datatables. It supports operations like renaming animals, excluding time ranges,
and applying binning.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Literal
from uuid import uuid7

import pandas as pd

from tse_analytics.core import messaging
from tse_analytics.core.color_manager import get_factor_level_color_hex
from tse_analytics.core.data.dafault_factor_builders import DEFAULT_FACTOR_BUILDERS
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.report import Report
from tse_analytics.core.data.shared import (
    Animal,
    ByTimeOfDayConfig,
    Factor,
    FactorLevel,
)
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem
from tse_analytics.core.models.datatable_tree_item import DatatableTreeItem
from tse_analytics.core.models.report_tree_item import ReportTreeItem
from tse_analytics.core.models.tree_item import TreeItem

DatasetType = Literal["PhenoMaster", "IntelliMaze", "IntelliCage"]


def _time_interval_level_prefix(interval: timedelta) -> str:
    """Return the level-name prefix derived from the largest unit that
    divides ``interval`` evenly (``"Day"`` / ``"Hour"`` / ``"Minute"`` /
    ``"Second"``)."""
    total_seconds = int(interval.total_seconds())
    if total_seconds > 0 and total_seconds % 86400 == 0:
        return "Day"
    if total_seconds > 0 and total_seconds % 3600 == 0:
        return "Hour"
    if total_seconds > 0 and total_seconds % 60 == 0:
        return "Minute"
    return "Second"


class Dataset:
    """
    A class representing an experimental dataset.

    The Dataset class manages experimental data, including metadata, animals, factors,
    and datatables. It provides methods for manipulating the dataset, such as renaming
    animals, excluding time ranges, and applying binning.
    """

    def __init__(
        self,
        name: str,
        description: str,
        dataset_type: DatasetType,
        metadata: dict[str, Any],
        animals: dict[str, Animal],
    ):
        """
        Initialize a Dataset instance.

        Parameters
        ----------
        name : str
            Name of the dataset.
        description : str
            Description of the dataset.
        dataset_type : DatasetType
            Source platform of the dataset (PhenoMaster / IntelliMaze / IntelliCage).
        metadata : dict[str, Any]
            Metadata describing the dataset, including name, description, and experiment times.
        animals : dict[str, Animal]
            Dictionary mapping animal IDs to Animal objects.
        """
        self.id = uuid7()
        self.name = name
        self.description = description
        self.dataset_type = dataset_type
        self.metadata = metadata
        self.animals = animals

        # Subject column for repeated-measures stats (pingouin's ``subject=``); loaders may override.
        self.subject_id_column: str = "Animal"

        self.datatables: dict[str, Datatable] = {}
        self.raw_datatables: dict[str, dict[str, Datatable]] = {}

        self.factors: dict[str, Factor] = {}
        self._ensure_default_factors()

        self.reports: dict[str, Report] = {}

    @property
    def light_cycles(self) -> ByTimeOfDayConfig:
        """Configuration for the dataset's light/dark cycle.

        Returns the LightCycle factor's ``ByTimeOfDayConfig``. Consumers read
        ``light_cycle_start`` and ``dark_cycle_start``.
        """
        factor = self.factors["LightCycle"]
        assert isinstance(factor.config, ByTimeOfDayConfig)
        return factor.config

    @property
    def source_path(self) -> str:
        """
        Get the source path of the dataset.

        Returns
        -------
        str
            The source path of the dataset from metadata, or an empty string if not available.
        """
        return self.metadata.get("source_path", "")

    @property
    def runs(self) -> int:
        """
        Get the number of runs in the dataset.
        """
        return len(self.metadata["runs"]) if "runs" in self.metadata else 1

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

    def _iter_all_datatables(self) -> Iterator[Datatable]:
        """Yield every datatable owned by this dataset (regular first, then raw)."""
        yield from self.datatables.values()
        for extension_datatables in self.raw_datatables.values():
            yield from extension_datatables.values()

    def _ensure_default_factors(self) -> None:
        """Add any missing built-in factors (Animal / Total / LightCycle)."""
        for name, build in DEFAULT_FACTOR_BUILDERS.items():
            if name not in self.factors:
                self.factors[name] = build(self)

    def add_datatable(self, datatable: Datatable) -> None:
        """
        Add a datatable to the dataset.

        Parameters
        ----------
        datatable : Datatable
            The datatable to add to the dataset.
        """
        self.datatables[datatable.name] = datatable

    def add_raw_datatable(self, extension_name: str, datatable: Datatable) -> None:
        """
        Add raw datatable to the dataset.

        Parameters
        ----------
        extension_name : str
            Name of the extension that created the datatable.
        datatable : Datatable
            The raw datatable to add to the dataset.
        """
        datatable.metadata["extension_name"] = extension_name
        if extension_name not in self.raw_datatables:
            self.raw_datatables[extension_name] = {}
        self.raw_datatables[extension_name][datatable.name] = datatable

    def remove_datatable(self, datatable: Datatable) -> None:
        """
        Remove a datatable from the dataset.

        Parameters
        ----------
        datatable : Datatable
            The datatable to remove from the dataset.
        """
        if datatable.extension_name is not None:
            self.raw_datatables[datatable.extension_name].pop(datatable.name)
        else:
            self.datatables.pop(datatable.name)

    def rename(self, name: str) -> None:
        """
        Rename the dataset.

        Parameters
        ----------
        name : str
            The new name for the dataset.
        """
        self.name = name

    def extract_levels_from_property(self, property_name: str) -> dict[str, FactorLevel]:
        """
        Extract factor levels from an animal property.

        Animals lacking ``property_name`` are bucketed into a synthetic
        ``"Missing"`` level. If no animal has the property, an empty dict is
        returned.

        Parameters
        ----------
        property_name : str
            The name of the animal property to extract levels from.

        Returns
        -------
        dict[str, FactorLevel]
            A dictionary mapping level names to FactorLevel objects, sorted
            case-insensitively by name.
        """
        levels_dict: dict[str, list[str]] = {}
        missing_ids: list[str] = []
        for animal in self.animals.values():
            if property_name not in animal.properties:
                missing_ids.append(animal.id)
                continue
            level_name = str(animal.properties[property_name])
            levels_dict.setdefault(level_name, []).append(animal.id)

        if not levels_dict:
            return {}

        if missing_ids:
            levels_dict["Missing"] = missing_ids

        levels: dict[str, FactorLevel] = {}
        for index, (key, value) in enumerate(levels_dict.items()):
            levels[key] = FactorLevel(
                name=key,
                color=get_factor_level_color_hex(index),
                animal_ids=value,
            )

        return dict(sorted(levels.items(), key=lambda x: x[0].lower()))

    def extract_levels_from_column(self, column_name: str) -> dict[str, FactorLevel]:
        """
        Extract factor levels from the unique values of a datatable column.

        Levels are derived from the first datatable that contains the column. NA
        values are dropped, and remaining values are coerced to strings to form
        level names.

        Parameters
        ----------
        column_name : str
            Name of the column to extract levels from.

        Returns
        -------
        dict[str, FactorLevel]
            A dictionary mapping level names to FactorLevel objects, sorted
            case-insensitively by name. Empty if no datatable contains the column.
        """
        levels: dict[str, FactorLevel] = {}
        for datatable in self.datatables.values():
            if column_name in datatable.df.columns:
                series = datatable.df[column_name].dropna()
                unique_values = (
                    series.unique().tolist() if series.dtype.name != "category" else list(series.cat.categories)
                )
                for index, value in enumerate(unique_values):
                    level_name = str(value)
                    levels[level_name] = FactorLevel(
                        name=level_name,
                        color=get_factor_level_color_hex(index),
                    )
                break

        levels = dict(sorted(levels.items(), key=lambda x: x[0].lower()))
        return levels

    def extract_levels_from_time_interval(self, interval: timedelta) -> dict[str, FactorLevel]:
        """
        Build factor levels for a ``BY_TIME_INTERVAL`` factor.

        One level is generated per bin spanned by the dataset's ``Timedelta``
        range at the requested ``interval``. Level names use a unit-derived
        prefix (``"Day"``, ``"Hour"``, ``"Minute"``, ``"Second"``) followed by
        the zero-based bin index, e.g. ``"Day 0"``, ``"Day 1"``. Colors are
        assigned sequentially via ``get_factor_level_color_hex``.

        Parameters
        ----------
        interval : timedelta
            The width of each bin. Must be positive.

        Returns
        -------
        dict[str, FactorLevel]
            Mapping of level name to FactorLevel, in numeric (insertion) order.
            Empty if ``interval`` is non-positive or no datatable exposes a
            usable ``Timedelta`` column.
        """
        levels: dict[str, FactorLevel] = {}
        interval_td = pd.Timedelta(interval)
        if interval_td <= pd.Timedelta(0):
            return levels

        max_timedelta: pd.Timedelta | None = None
        for datatable in self.datatables.values():
            if "Timedelta" not in datatable.df.columns:
                continue
            series = datatable.df["Timedelta"].dropna()
            if series.empty:
                continue
            max_timedelta = pd.Timedelta(series.max())
            break

        if max_timedelta is None or max_timedelta < pd.Timedelta(0):
            return levels

        num_bins = int(max_timedelta // interval_td) + 1
        prefix = _time_interval_level_prefix(interval)
        for index in range(num_bins):
            level_name = f"{prefix} {index}"
            levels[level_name] = FactorLevel(
                name=level_name,
                color=get_factor_level_color_hex(index),
            )
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

        for datatable in self._iter_all_datatables():
            datatable.rename_animal(old_id, animal)

        # Rename animal in factor's levels definitions
        for factor in self.factors.values():
            for level in factor.levels.values():
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

        messaging.broadcast(messaging.DatasetChangedMessage(sender=self, dataset=self))

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
            for level in factor.levels.values():
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

        for datatable in self._iter_all_datatables():
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

        for datatable in self._iter_all_datatables():
            datatable.exclude_time(range_start, range_end)

        # Re-materialize factor columns whose values depend on Timedelta
        # (Bin via ByTimeIntervalConfig, named phases via ByElapsedTimeConfig).
        self.set_factors(self.factors)

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

        for datatable in self._iter_all_datatables():
            datatable.trim_time(range_start, range_end)

        # Re-materialize factor columns whose values depend on Timedelta.
        self.set_factors(self.factors)

    def resample(self, resample_interval: pd.Timedelta) -> None:
        """
        Resample all datatables in the dataset.

        This method applies the specified resampling interval to all datatables
        in the dataset.

        Parameters
        ----------
        resample_interval : pd.Timedelta
            The time interval to resample the data to.
        """
        for datatable in self.datatables.values():
            datatable.resample(resample_interval)

    def set_factors(
        self,
        factors: dict[str, Factor],
        old_factor_names: Iterable[str] | None = None,
    ) -> None:
        """
        Set the factors for the dataset.

        This method updates the factors in the dataset and applies them to all datatables.

        Parameters
        ----------
        factors : dict[str, Factor]
            Dictionary mapping factor names to Factor objects.
        old_factor_names : Iterable[str] | None
            Names of previously applied factors; their materialized columns are
            dropped from each datatable before re-applying. ``"Animal"`` and
            ``"Run"`` are preserved by ``Datatable.set_factors``.
        """
        self.factors = factors
        self._ensure_default_factors()

        for datatable in self.datatables.values():
            datatable.set_factors(factors, old_factor_names)

    def clone(self) -> Dataset:
        """
        Create a deep copy of the dataset.

        Uses ``Datatable.clone()`` (which uses pandas' ``df.copy()``) for each
        datatable instead of ``copy.deepcopy``, which is significantly faster
        for large dataframes.

        Returns
        -------
        Dataset
            A new Dataset instance that is a deep copy of this dataset.
        """
        new = Dataset(
            name=self.name,
            description=self.description,
            dataset_type=self.dataset_type,
            metadata=deepcopy(self.metadata),
            animals=deepcopy(self.animals),
        )
        new.subject_id_column = self.subject_id_column
        new.factors = deepcopy(self.factors)
        new.reports = deepcopy(self.reports)

        new.datatables = {}
        for name, dt in self.datatables.items():
            cloned = dt.clone()
            cloned.dataset = new
            new.datatables[name] = cloned

        new.raw_datatables = {}
        for ext, tables in self.raw_datatables.items():
            new.raw_datatables[ext] = {}
            for name, dt in tables.items():
                cloned = dt.clone()
                cloned.dataset = new
                new.raw_datatables[ext][name] = cloned

        return new

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

        # Add datatables nodes
        for datatable in self.datatables.values():
            datatable_tree_item = DatatableTreeItem(datatable)
            dataset_tree_item.add_child(datatable_tree_item)

        # Add raw datatables nodes
        if len(self.raw_datatables) > 0:
            raw_datatables_node = TreeItem("Raw Data")
            dataset_tree_item.add_child(raw_datatables_node)
            for extension_name, extension_datatables in self.raw_datatables.items():
                if len(extension_datatables) > 0:
                    extension_node = TreeItem(extension_name)
                    raw_datatables_node.add_child(extension_node)
                    for datatable in extension_datatables.values():
                        raw_datatable_tree_item = DatatableTreeItem(datatable)
                        extension_node.add_child(raw_datatable_tree_item)

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
