"""System prompt builder for the AI Agent widget.

Produces a single cacheable text block describing a :class:`Datatable` —
schema, animals, factors, sample rows, domain hints, and a strict coding
contract — so Claude can generate pandas code against ``df``.
"""

from __future__ import annotations

from typing import Any

from tse_analytics.core.data.datatable import Datatable


def _format_variables(datatable: Datatable) -> str:
    if not datatable.variables:
        return "(none)"
    lines = []
    for var in datatable.variables.values():
        unit = f" [{var.unit}]" if var.unit else ""
        desc = f" — {var.description}" if var.description else ""
        lines.append(f"- {var.name}{unit} (agg={var.aggregation}){desc}")
    return "\n".join(lines)


def _format_animals(datatable: Datatable) -> str:
    animals = datatable.dataset.animals
    if not animals:
        return "(none)"
    lines = []
    for animal in animals.values():
        props = ", ".join(f"{k}={v}" for k, v in animal.properties.items()) if animal.properties else ""
        lines.append(f"- {animal.id}" + (f" ({props})" if props else ""))
    return "\n".join(lines)


def _format_factors(datatable: Datatable) -> str:
    factors = datatable.dataset.factors
    if not factors:
        return "(none)"
    lines = []
    for factor in factors.values():
        level_names = ", ".join(list(factor.levels.keys()))
        lines.append(f"- {factor.name}: [{level_names}]")
    return "\n".join(lines)


def _format_dtypes(datatable: Datatable) -> str:
    dtypes = datatable.df.dtypes.astype(str).to_dict()
    return "\n".join(f"- {col}: {dtype}" for col, dtype in dtypes.items())


def _format_metadata(datatable: Datatable) -> str:
    parts = [
        f"Dataset name: {datatable.dataset.name}",
        f"Dataset type: {datatable.dataset.dataset_type}",
        f"Datatable name: {datatable.name}",
        f"Rows: {len(datatable.df):,}",
        f"Columns: {len(datatable.df.columns)}",
    ]
    if datatable.sample_interval is not None:
        parts.append(f"Sample interval: {datatable.sample_interval}")
    try:
        parts.append(f"Duration: {datatable.duration}")
    except Exception:
        pass
    return "\n".join(parts)


def build_system_prompt(datatable: Datatable) -> list[dict[str, Any]]:
    """Build the system prompt for an AI Agent conversation.

    Returns a single cacheable text block describing the datatable so Claude
    can write pandas code against the DataFrame ``df``.

    Args:
        datatable: The :class:`Datatable` the user is querying.

    Returns:
        A list with one dict suitable for the ``system`` parameter of
        ``anthropic.messages.create``. The block carries
        ``cache_control={"type": "ephemeral"}`` for prompt-cache reuse.
    """
    head_text = datatable.df.head(10).to_string(max_cols=None)

    text = f"""You are a data-analysis assistant embedded in TSE Analytics, a PySide6 desktop
app for TSE PhenoMaster / IntelliCage / IntelliMaze experiments.

The user is exploring a single pandas DataFrame (`df`) loaded from a Datatable.
Answer questions about this DataFrame by generating pandas code.

# Dataset & Datatable

{_format_metadata(datatable)}

# Column dtypes

{_format_dtypes(datatable)}

# Variables (measured quantities)

{_format_variables(datatable)}

# Animals

{_format_animals(datatable)}

# Factors (experimental grouping)

{_format_factors(datatable)}

# First 10 rows of df

{head_text}

# Domain hints

- `DateTime` column is the absolute timestamp of each measurement.
- `Timedelta` column (when present) is a pandas Timedelta since the experiment started.
- `Bin` column (when present) is an integer bin index at the sample interval.
- `Animal` is the categorical identifier of the subject.
- Factor columns are categorical; their levels match the "Factors" section above.
- Numeric variable columns use pandas numpy-nullable dtypes (e.g. `Float64`, `Int64`),
  so missing values are `pd.NA`, not `NaN`. Aggregations should handle `pd.NA` gracefully.

# Coding contract

- Reply with a short plain-text explanation (1-3 sentences), then EXACTLY ONE
  fenced code block marked as ```python ... ``` containing the pandas code.
- Assign the final answer to a variable named `result`.
  - Tables → pandas DataFrame or Series (Series are shown as single-column tables).
  - Plots → a `matplotlib.figure.Figure` (do NOT call `plt.show()`).
  - Scalars → int/float/str.
- Available names in the execution namespace: `df` (the DataFrame), `pd` (pandas),
  `np` (numpy), `plt` (matplotlib.pyplot). Do not import other modules, read files,
  or access the network.
- Treat `df` as read-only. If you need to modify, call `.copy()` first.
- Prefer vectorised pandas operations over Python loops.
- Keep code concise (aim for under ~30 lines). No print statements.
- For plots: build the figure with `fig, ax = plt.subplots()` and assign
  `result = fig`. Do NOT call `plt.show()`.
"""

    return [
        {
            "type": "text",
            "text": text,
            "cache_control": {"type": "ephemeral"},
        }
    ]
