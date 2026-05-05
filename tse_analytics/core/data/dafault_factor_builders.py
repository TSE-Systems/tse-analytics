from __future__ import annotations

from collections.abc import Callable
from datetime import time
from typing import TYPE_CHECKING

from tse_analytics.core.color_manager import get_color_hex, get_factor_level_color_hex
from tse_analytics.core.data.shared import Animal, ByAnimalConfig, ByTimeOfDayConfig, Factor, FactorLevel, FactorRole

if TYPE_CHECKING:
    from tse_analytics.core.data.dataset import Dataset


def _get_default_animal_factor(animals: dict[str, Animal]) -> Factor:
    levels = {}
    for i, animal in enumerate(animals.values()):
        levels[animal.id] = FactorLevel(
            name=animal.id,
            color=get_color_hex(i),
            animal_ids=[animal.id],
        )
    return Factor(
        name="Animal",
        role=FactorRole.BETWEEN_SUBJECT,
        config=ByAnimalConfig(),
        levels=levels,
    )


def _get_default_total_factor(animals: dict[str, Animal]) -> Factor:
    return Factor(
        name="Total",
        role=FactorRole.BETWEEN_SUBJECT,
        config=ByAnimalConfig(),
        levels={
            "All animals": FactorLevel(
                name="All animals", color=get_factor_level_color_hex(0), animal_ids=list(animals.keys())
            ),
        },
    )


def _get_default_light_cycle_factor() -> Factor:
    return Factor(
        name="LightCycle",
        role=FactorRole.WITHIN_SUBJECT,
        config=ByTimeOfDayConfig(
            light_cycle_start=time(7, 0),
            dark_cycle_start=time(19, 0),
        ),
        levels={
            "Light": FactorLevel(name="Light", color=get_factor_level_color_hex(1)),
            "Dark": FactorLevel(name="Dark", color=get_factor_level_color_hex(0)),
        },
    )


DEFAULT_FACTOR_BUILDERS: dict[str, Callable[[Dataset], Factor]] = {
    "Animal": lambda ds: _get_default_animal_factor(ds.animals),
    "Total": lambda ds: _get_default_total_factor(ds.animals),
    "LightCycle": lambda ds: _get_default_light_cycle_factor(),
}
