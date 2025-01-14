from datetime import datetime
from typing import Protocol
from uuid import UUID

import pandas as pd

from tse_analytics.core.data.binning import BinningSettings
from tse_analytics.core.data.outliers import OutliersSettings
from tse_analytics.core.data.shared import Animal, Factor, SplitMode, Variable
from tse_analytics.core.models.dataset_tree_item import DatasetTreeItem


class Dataset(Protocol):
    id: UUID
    name: str
    path: str
    meta: dict | list[dict]

    animals: dict[str, Animal]
    variables: dict[str, Variable]

    original_df: pd.DataFrame
    active_df: pd.DataFrame
    sampling_interval: pd.Timedelta

    factors: dict[str, Factor]

    outliers_settings: OutliersSettings
    binning_settings: BinningSettings

    report: str

    @property
    def start_timestamp(self) -> pd.Timestamp: ...

    @property
    def end_timestamp(self) -> pd.Timestamp: ...

    @property
    def duration(self) -> pd.Timedelta: ...

    def rename_animal(self, old_id: str, animal: Animal) -> None: ...

    def exclude_animals(self, animal_ids: set[str]) -> None: ...

    def exclude_time(self, range_start: datetime, range_end: datetime) -> None: ...

    def trim_time(self, range_start: datetime, range_end: datetime) -> None: ...

    def resample(self, resampling_interval: pd.Timedelta) -> None: ...

    def adjust_time(self, delta: pd.Timedelta) -> None: ...

    def set_factors(self, factors: dict[str, Factor]) -> None: ...

    def refresh_active_df(self) -> None: ...

    def get_current_df(
        self,
        variables: dict[str, Variable] | None = None,
        split_mode=SplitMode.ANIMAL,
        selected_factor_name: str | None = None,
        dropna=False,
    ) -> pd.DataFrame: ...

    def get_data_table_df(
        self,
        variables: dict[str, Variable],
        split_mode: SplitMode,
        selected_factor_name: str,
    ) -> pd.DataFrame: ...

    def get_timeline_plot_df(
        self,
        variable: Variable,
        split_mode: SplitMode,
        selected_factor_name: str,
        calculate_errors: str | None,
    ) -> pd.DataFrame: ...

    def get_bar_plot_df(
        self,
        variable: Variable,
    ) -> pd.DataFrame: ...

    def get_anova_df(
        self,
        variables: dict[str, Variable],
    ) -> pd.DataFrame: ...

    def get_timeseries_df(
        self,
        animal: Animal,
        variable: Variable,
    ) -> pd.DataFrame: ...

    def export_to_excel(self, path: str) -> None: ...

    def export_to_csv(self, path: str) -> None: ...

    def apply_binning(self, binning_settings: BinningSettings) -> None: ...

    def apply_outliers(self, settings: OutliersSettings) -> None: ...

    def clone(self): ...

    def add_children_tree_items(self, dataset_tree_item: DatasetTreeItem) -> None: ...
