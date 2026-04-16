from datetime import datetime

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import Animal, Factor


def set_factors_recursively(
    datatable: Datatable,
    factors: dict[str, Factor],
    old_factors: dict[str, Factor] | None = None,
) -> None:
    datatable.set_factors(factors, old_factors)
    for derived_table in datatable.derived_tables.values():
        set_factors_recursively(derived_table, factors, old_factors)


def rename_animal_recursively(datatable: Datatable, old_id: str, animal: Animal) -> None:
    datatable.rename_animal(old_id, animal)
    for derived_table in datatable.derived_tables.values():
        rename_animal_recursively(derived_table, old_id, animal)


def trim_time_recursively(datatable: Datatable, range_start: datetime, range_end: datetime) -> None:
    datatable.trim_time(range_start, range_end)
    for derived_table in datatable.derived_tables.values():
        trim_time_recursively(derived_table, range_start, range_end)


def exclude_time_recursively(datatable: Datatable, range_start: datetime, range_end: datetime) -> None:
    datatable.exclude_time(range_start, range_end)
    for derived_table in datatable.derived_tables.values():
        exclude_time_recursively(derived_table, range_start, range_end)


def exclude_animals_recursively(datatable: Datatable, animal_ids: set[str]) -> None:
    datatable.exclude_animals(animal_ids)
    for derived_table in datatable.derived_tables.values():
        exclude_animals_recursively(derived_table, animal_ids)
