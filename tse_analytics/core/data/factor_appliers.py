"""
Factor applier functions and dispatch table.

Each applier takes a dataframe, a Factor, and the owning Dataset, and
materializes a new categorical column on the dataframe. ``FACTOR_APPLIERS``
maps each ``FactorConfig`` subtype to its applier; adding a new factor
source means registering a new entry here and (if needed) defining a new
config dataclass in ``shared.py``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from loguru import logger

from tse_analytics.core.data.shared import (
    ByAnimalConfig,
    ByAnimalPropertyConfig,
    ByColumnConfig,
    ByElapsedTimeConfig,
    ByTimeIntervalConfig,
    ByTimeOfDayConfig,
    Factor,
)

if TYPE_CHECKING:
    from tse_analytics.core.data.dataset import Dataset


def _apply_animal_map(df: pd.DataFrame, factor: Factor, animal_factor_map: dict[str, Any]) -> None:
    series = df["Animal"].astype("string").map(animal_factor_map)
    categories = sorted(
        {v for v in animal_factor_map.values() if pd.notna(v)},
        key=str.lower,
    )
    df[factor.name] = pd.Categorical(series, categories=categories)


def _apply_by_animal(df: pd.DataFrame, factor: Factor, dataset: Dataset) -> None:
    animal_factor_map: dict[str, Any] = dict.fromkeys(df["Animal"].unique(), pd.NA)
    for level in factor.levels.values():
        for animal_id in level.animal_ids:
            animal_factor_map[animal_id] = level.name
    _apply_animal_map(df, factor, animal_factor_map)


def _apply_by_animal_property(df: pd.DataFrame, factor: Factor, dataset: Dataset) -> None:
    cfg = factor.config
    assert isinstance(cfg, ByAnimalPropertyConfig)

    animal_factor_map: dict[str, Any] = dict.fromkeys(df["Animal"].unique(), pd.NA)
    for animal in dataset.animals.values():
        if cfg.property_key in animal.properties:
            animal_factor_map[animal.id] = str(animal.properties[cfg.property_key])
    _apply_animal_map(df, factor, animal_factor_map)


def _apply_by_time_of_day(df: pd.DataFrame, factor: Factor, dataset: Dataset) -> None:
    cfg = factor.config
    assert isinstance(cfg, ByTimeOfDayConfig)
    if "DateTime" not in df.columns:
        logger.debug(f"Skipping factor {factor.name!r}: no DateTime column")
        return

    light_start = cfg.light_cycle_start
    dark_start = cfg.dark_cycle_start

    times = df["DateTime"].dt.time
    is_light = (times >= light_start) & (times < dark_start)
    df[factor.name] = pd.Categorical(
        np.where(is_light, "Light", "Dark"),
        categories=["Light", "Dark"],
        ordered=True,
    )


def _apply_by_elapsed_time(df: pd.DataFrame, factor: Factor, dataset: Dataset) -> None:
    cfg = factor.config
    assert isinstance(cfg, ByElapsedTimeConfig)
    if len(cfg.phases) == 0:
        logger.debug(f"Skipping factor {factor.name!r}: no phases configured")
        return
    if "Timedelta" not in df.columns:
        logger.debug(f"Skipping factor {factor.name!r}: no Timedelta column")
        return

    phases = sorted(cfg.phases, key=lambda p: p.start_timestamp)
    edges = [pd.Timedelta(p.start_timestamp) for p in phases]
    edges.append(pd.Timedelta.max)
    labels = [p.name for p in phases]
    df[factor.name] = pd.cut(
        df["Timedelta"],
        bins=edges,
        labels=labels,
        right=False,
        ordered=True,
    )


def _apply_by_column(df: pd.DataFrame, factor: Factor, dataset: Dataset) -> None:
    cfg = factor.config
    assert isinstance(cfg, ByColumnConfig)
    if cfg.column not in df.columns:
        logger.debug(f"Skipping factor {factor.name!r}: source column {cfg.column!r} not present")
        return

    series = df[cfg.column]
    df[factor.name] = series if series.dtype.name == "category" else series.astype("category")


def _apply_by_time_interval(df: pd.DataFrame, factor: Factor, dataset: Dataset) -> None:
    cfg = factor.config
    assert isinstance(cfg, ByTimeIntervalConfig)
    if "Timedelta" not in df.columns:
        logger.debug(f"Skipping factor {factor.name!r}: no Timedelta column")
        return
    interval_td = pd.Timedelta(cfg.interval)
    if interval_td <= pd.Timedelta(0):
        logger.debug(f"Skipping factor {factor.name!r}: non-positive interval {interval_td!r}")
        return

    if not factor.levels:
        factor.levels = dataset.extract_levels_from_time_interval(cfg.interval)
    if not factor.levels:
        logger.debug(f"Skipping factor {factor.name!r}: no levels could be derived")
        return

    bin_indices = (df["Timedelta"] // interval_td).astype("Int64")
    name_for = {i: lvl.name for i, lvl in enumerate(factor.levels.values())}
    df[factor.name] = bin_indices.map(name_for)
    categories = [lvl.name for lvl in factor.levels.values()]
    df[factor.name] = df[factor.name].astype("category").cat.set_categories(categories, ordered=True)


FactorApplier = Callable[[pd.DataFrame, Factor, "Dataset"], None]

FACTOR_APPLIERS: dict[type, FactorApplier] = {
    ByAnimalConfig: _apply_by_animal,
    ByAnimalPropertyConfig: _apply_by_animal_property,
    ByTimeOfDayConfig: _apply_by_time_of_day,
    ByElapsedTimeConfig: _apply_by_elapsed_time,
    ByColumnConfig: _apply_by_column,
    ByTimeIntervalConfig: _apply_by_time_interval,
}
