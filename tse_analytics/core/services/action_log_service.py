"""Recording API for the per-Dataset analysis log.

UI chokepoints (dialogs, toolbox actions) call the helpers in this module to
append a new ``AnalysisAction`` to ``Dataset.analysis_log`` after performing
the corresponding mutation. Each helper wraps the underlying mutation's
arguments into the matching action variant, sets the timestamp/sequence, and
broadcasts ``AnalysisLogChangedMessage``.
"""

from __future__ import annotations

from datetime import datetime

from tse_analytics.core import messaging
from tse_analytics.core.data.analysis_log import (
    AnalysisAction,
    CreateDerivedDatatableAction,
    ExcludeAnimalsAction,
    ExcludeTimeAction,
    RenameAnimalAction,
    SetFactorsAction,
    TrimTimeAction,
)
from tse_analytics.core.data.binning import TimeIntervalsBinningSettings
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Animal, Factor


def record_action(sender: object, dataset: Dataset, action: AnalysisAction) -> None:
    """Append ``action`` to ``dataset.analysis_log`` and broadcast a change message."""
    dataset.analysis_log.append(action)
    messaging.broadcast(messaging.AnalysisLogChangedMessage(sender, dataset, action))


def _next_sequence(dataset: Dataset) -> int:
    return len(dataset.analysis_log)


def record_create_derived_datatable(
    sender: object,
    dataset: Dataset,
    *,
    source_datatable_name: str,
    target_datatable_name: str,
    target_description: str,
    excluded_animal_ids: set[str],
    binning: TimeIntervalsBinningSettings | None,
) -> None:
    parts: list[str] = [f"Derived '{target_datatable_name}' from '{source_datatable_name}'"]
    if excluded_animal_ids:
        parts.append(f"excluded {len(excluded_animal_ids)} animal(s)")
    if binning is not None:
        parts.append(f"binned by {binning.delta} {binning.unit}")
    action = CreateDerivedDatatableAction(
        timestamp=datetime.now(),
        sequence=_next_sequence(dataset),
        description="; ".join(parts),
        source_datatable_name=source_datatable_name,
        target_datatable_name=target_datatable_name,
        target_description=target_description,
        excluded_animal_ids=sorted(excluded_animal_ids),
        binning=binning,
    )
    record_action(sender, dataset, action)


def record_set_factors(
    sender: object,
    dataset: Dataset,
    factors: dict[str, Factor],
) -> None:
    action = SetFactorsAction(
        timestamp=datetime.now(),
        sequence=_next_sequence(dataset),
        description=f"Set factors: {', '.join(sorted(factors.keys())) or '(none)'}",
        factors=factors,
    )
    record_action(sender, dataset, action)


def record_exclude_animals(
    sender: object,
    dataset: Dataset,
    animal_ids: set[str],
) -> None:
    sorted_ids = sorted(animal_ids)
    action = ExcludeAnimalsAction(
        timestamp=datetime.now(),
        sequence=_next_sequence(dataset),
        description=f"Excluded animals: {', '.join(sorted_ids)}",
        animal_ids=sorted_ids,
    )
    record_action(sender, dataset, action)


def record_exclude_time(
    sender: object,
    dataset: Dataset,
    range_start: datetime,
    range_end: datetime,
) -> None:
    action = ExcludeTimeAction(
        timestamp=datetime.now(),
        sequence=_next_sequence(dataset),
        description=f"Excluded time range {range_start.isoformat()} – {range_end.isoformat()}",
        range_start=range_start,
        range_end=range_end,
    )
    record_action(sender, dataset, action)


def record_trim_time(
    sender: object,
    dataset: Dataset,
    range_start: datetime,
    range_end: datetime,
) -> None:
    action = TrimTimeAction(
        timestamp=datetime.now(),
        sequence=_next_sequence(dataset),
        description=f"Trimmed to {range_start.isoformat()} – {range_end.isoformat()}",
        range_start=range_start,
        range_end=range_end,
    )
    record_action(sender, dataset, action)


def record_rename_animal(
    sender: object,
    dataset: Dataset,
    old_id: str,
    new_animal: Animal,
) -> None:
    action = RenameAnimalAction(
        timestamp=datetime.now(),
        sequence=_next_sequence(dataset),
        description=f"Renamed animal '{old_id}' → '{new_animal.id}'",
        old_id=old_id,
        new_animal=new_animal,
    )
    record_action(sender, dataset, action)
