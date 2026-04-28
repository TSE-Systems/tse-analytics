"""Per-action Python code generation for notebook export.

Each function takes an ``AnalysisAction`` variant and returns the Python source
code for one notebook cell that re-applies the action against an in-memory
``Dataset`` named ``dataset``. The dispatch dict maps an action ``kind`` to its
generator.
"""

from __future__ import annotations

from collections.abc import Callable

from pydantic import TypeAdapter

from tse_analytics.core.data.analysis_log import (
    AnalysisAction,
    CreateDerivedDatatableAction,
    ExcludeAnimalsAction,
    ExcludeTimeAction,
    RenameAnimalAction,
    SetFactorsAction,
    TrimTimeAction,
)
from tse_analytics.core.data.shared import Animal, Factor


def _format_dict_literal(data: dict | list, indent: int = 4) -> str:
    """Render a JSON-compatible dict/list as a multi-line Python literal."""
    import pprint

    return pprint.pformat(data, indent=indent, width=100, sort_dicts=False)


def codegen_create_derived_datatable(action: CreateDerivedDatatableAction) -> str:
    excluded = sorted(action.excluded_animal_ids)
    excluded_repr = "set()" if not excluded else "{" + ", ".join(repr(a) for a in excluded) + "}"
    if action.binning is None:
        binning_repr = "None"
    else:
        binning_repr = (
            f'TimeIntervalsBinningSettings(unit={action.binning.unit!r}, '
            f"delta={action.binning.delta})"
        )
    return (
        f"# {action.description}\n"
        f"source_dt = dataset.datatables[{action.source_datatable_name!r}]\n"
        f"derived = Datatable(\n"
        f"    dataset=dataset,\n"
        f"    name={action.target_datatable_name!r},\n"
        f"    description={action.target_description!r},\n"
        f"    variables=source_dt.variables.copy(),\n"
        f"    df=source_dt.df.copy(),\n"
        f"    metadata=source_dt.metadata.copy(),\n"
        f")\n"
        f"process_table(derived, excluded_animal_ids={excluded_repr}, "
        f"time_intervals_settings={binning_repr})\n"
        f"dataset.add_datatable(derived)"
    )


def codegen_set_factors(action: SetFactorsAction) -> str:
    factors_dump = TypeAdapter(dict[str, Factor]).dump_python(action.factors, mode="json")
    factors_literal = _format_dict_literal(factors_dump)
    return (
        f"# {action.description}\n"
        f"factors_payload = {factors_literal}\n"
        f"factors = TypeAdapter(dict[str, Factor]).validate_python(factors_payload)\n"
        f"dataset.set_factors(factors, dataset.factors)"
    )


def codegen_exclude_animals(action: ExcludeAnimalsAction) -> str:
    ids_repr = "{" + ", ".join(repr(a) for a in action.animal_ids) + "}" if action.animal_ids else "set()"
    return (
        f"# {action.description}\n"
        f"dataset.exclude_animals({ids_repr})"
    )


def codegen_exclude_time(action: ExcludeTimeAction) -> str:
    return (
        f"# {action.description}\n"
        f"dataset.exclude_time(\n"
        f"    datetime.fromisoformat({action.range_start.isoformat()!r}),\n"
        f"    datetime.fromisoformat({action.range_end.isoformat()!r}),\n"
        f")"
    )


def codegen_trim_time(action: TrimTimeAction) -> str:
    return (
        f"# {action.description}\n"
        f"dataset.trim_time(\n"
        f"    datetime.fromisoformat({action.range_start.isoformat()!r}),\n"
        f"    datetime.fromisoformat({action.range_end.isoformat()!r}),\n"
        f")"
    )


def codegen_rename_animal(action: RenameAnimalAction) -> str:
    animal_dump = TypeAdapter(Animal).dump_python(action.new_animal, mode="json")
    animal_literal = _format_dict_literal(animal_dump)
    return (
        f"# {action.description}\n"
        f"new_animal = TypeAdapter(Animal).validate_python({animal_literal})\n"
        f"dataset.rename_animal({action.old_id!r}, new_animal)"
    )


_DISPATCH: dict[str, Callable[..., str]] = {
    "create_derived_datatable": codegen_create_derived_datatable,
    "set_factors": codegen_set_factors,
    "exclude_animals": codegen_exclude_animals,
    "exclude_time": codegen_exclude_time,
    "trim_time": codegen_trim_time,
    "rename_animal": codegen_rename_animal,
}


def codegen_for_action(action: AnalysisAction) -> str:
    """Return the Python source for re-applying a single ``AnalysisAction``."""
    return _DISPATCH[action.kind](action)
