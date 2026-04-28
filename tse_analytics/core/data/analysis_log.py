"""Append-only analysis log used to make every dataset mutation reproducible.

Each entry is a serializable description of one user-driven action that mutates
the dataset (binning, factor edits, animal exclusion, time trimming, etc.).
Replaying entries in order against a freshly-loaded raw dataset reproduces the
session state.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field
from pydantic.dataclasses import dataclass

from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.shared import Animal, Factor


@dataclass
class CreateDerivedDatatableAction:
    """A new datatable was derived from another (animal exclusion + binning)."""

    timestamp: datetime
    sequence: int
    description: str
    source_datatable_name: str
    target_datatable_name: str
    target_description: str
    excluded_animal_ids: list[str]
    binning: TimeIntervalsBinningSettings | None = None
    kind: Literal["create_derived_datatable"] = "create_derived_datatable"


@dataclass
class SetFactorsAction:
    """The dataset's factors dict was wholesale replaced."""

    timestamp: datetime
    sequence: int
    description: str
    factors: dict[str, Factor]
    kind: Literal["set_factors"] = "set_factors"


@dataclass
class ExcludeAnimalsAction:
    """One or more animals were excluded from the dataset."""

    timestamp: datetime
    sequence: int
    description: str
    animal_ids: list[str]
    kind: Literal["exclude_animals"] = "exclude_animals"


@dataclass
class ExcludeTimeAction:
    """A time range was excluded from the dataset."""

    timestamp: datetime
    sequence: int
    description: str
    range_start: datetime
    range_end: datetime
    kind: Literal["exclude_time"] = "exclude_time"


@dataclass
class TrimTimeAction:
    """The dataset was trimmed to a time range."""

    timestamp: datetime
    sequence: int
    description: str
    range_start: datetime
    range_end: datetime
    kind: Literal["trim_time"] = "trim_time"


@dataclass
class RenameAnimalAction:
    """An animal was renamed (id changed)."""

    timestamp: datetime
    sequence: int
    description: str
    old_id: str
    new_animal: Animal
    kind: Literal["rename_animal"] = "rename_animal"


AnalysisAction = Annotated[
    CreateDerivedDatatableAction | SetFactorsAction | ExcludeAnimalsAction | ExcludeTimeAction | TrimTimeAction | RenameAnimalAction,
    Field(discriminator="kind"),
]
