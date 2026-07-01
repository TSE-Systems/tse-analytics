# 14 — The universal datatable

[← Back to index](README.md)

A [`Datatable`](05-data-model.md#datatable) is not only what a dataset is *imported* into — it is also
the unit any toolbox widget or extension can *generate* and push **back** into the dataset, so a
result becomes the input to a further analysis. Chronobiology's per-animal parameter table can feed
an ANOVA; DrinkFeed's interval table is itself a regular time series that binning and plots consume.

This page documents that "universal datatable" contract: the shared builder
(`Datatable.from_dataframe`), the metadata keys, and the difference between a **regular time series**
and a **cross-sectional** result table (and the guards that keep the latter safe).

**Source:** `core/data/datatable.py` (`Datatable.from_dataframe`, the `META_*` constants, the
`is_timeseries` guard). Reference producers: `toolbox/chronobiology/processor.py`
(`ResultTable.to_datatable`) and `modules/phenomaster/extensions/drinkfeed/`
(`interval_processor.py`, `sequential_processor.py`).

---

## Two shapes of datatable

| Shape | Has `DateTime`/`Timedelta`? | `is_timeseries` | `is_regular_timeseries` | Example |
|-------|-----------------------------|-----------------|-------------------------|---------|
| **Regular time series** | yes | `True` | `True` when `sample_interval` is set | imported `Main` table, `DrinkFeedIntervals` |
| **Irregular time series** | yes | `True` | `False` | event tables (`DrinkFeedEvents`) |
| **Cross-sectional** | no | `False` | `False` | per-animal chronobiology parameters, per-group summaries |

`Datatable` was originally written assuming the first shape (standard `Animal`/`DateTime`/`Timedelta`
columns). The toolbox now generates the third shape too — one row per animal or per group, no time
axis — so the class must tolerate the absence of a time axis. See [Guards](#time-axis-guards).

---

## The builder — `Datatable.from_dataframe`

Prefer this classmethod over calling `Datatable(...)` directly whenever you turn an analysis result
into a datatable. It centralizes the boilerplate that generation sites used to duplicate:
dtype-normalization, casting the identifier column to `category`, building `Variable` metadata,
recording provenance, and attaching factors.

```python
Datatable.from_dataframe(
    dataset, name, df, *,
    origin: str,                                    # -> metadata[META_ORIGIN]; required
    description: str | None = None,                 # defaults to f"{origin} result: {name}"
    id_column: str | None = "Animal",               # cast to category; excluded from auto-variables
    variables: dict[str, Variable] | None = None,   # given => used verbatim (full control)
    aggregation: Aggregation = Aggregation.MEAN,    # default for auto-generated variables
    unit: str = "",                                 # default for auto-generated variables
    sample_interval: pd.Timedelta | None = None,    # set => regular time series
    extra_metadata: dict[str, Any] | None = None,   # merged into metadata (must be JSON-native)
    normalize_dtypes: bool = True,                  # df.convert_dtypes() (nullable house rule)
    apply_factors: bool = True,                     # set_factors(dataset.factors)
) -> Datatable
```

**Variables — two modes:**

- **Auto-generate** (default, `variables=None`): one `Variable` per *numeric, non-`id_column`*
  column, using `aggregation`/`unit` as the defaults. Best for homogeneous result tables
  (all-`MEAN` parameters).
- **Verbatim** (`variables={...}`): the dict is used as-is. Auto-generation is skipped, so helper
  columns you *don't* want treated as measurements (e.g. `Bin`) simply stay out of the dict.

**dtype normalization:** `normalize_dtypes=True` runs `df.convert_dtypes()` to obtain numpy-nullable
dtypes (the house rule). Note `convert_dtypes()` downcasts a whole-number float column to `Int64` —
harmless for results, but pass `normalize_dtypes=False` when the caller already controls dtypes and
must preserve them (e.g. DrinkFeed's `Bin` is `UInt64`).

The returned datatable is **not** added to the dataset — register it explicitly (see
[Registering the result](#registering-the-result)).

### Example — chronobiology (auto-generated variables)

`ResultTable.to_datatable` (in `toolbox/chronobiology/processor.py`) is a one-liner over the builder.
The result has an `"Animal"` id column and all-numeric parameter columns; factors attach (a no-op for
per-group tables that have no `"Animal"` column):

```python
def to_datatable(self, dataset: Dataset, name: str) -> Datatable:
    return Datatable.from_dataframe(
        dataset,
        name,
        self.df,
        origin="Chronobiology",
        description=f"Chronobiology result: {name}",
        id_column=self.id_column,
    )
```

### Example — DrinkFeed (verbatim variables, regular time series)

`interval_processor.py` supplies its own `Variable` dict (so `Bin` is excluded), marks the table a
regular time series via `sample_interval=`, and keeps its explicit dtypes:

```python
return Datatable.from_dataframe(
    datatable.dataset,
    "DrinkFeedIntervals",
    intervals_df,
    origin="DrinkFeedIntervals",
    description="Drink/Feed intervals datatable",
    variables=variables,  # full dict incl. caloric cols; keeps Bin out of variables
    sample_interval=timedelta,  # regular time series
    apply_factors=False,
    normalize_dtypes=False,  # preserve Bin=UInt64 and the existing nullable dtypes
)
```

---

## The metadata contract

`Datatable.metadata` is a free-form `dict[str, Any]`, but a few keys are load-bearing. Use the
constants from `core/data/datatable.py` instead of string literals — a mistyped key is silent
(a datatable whose interval was stored under `"samping_interval"` reported `is_regular_timeseries ==
False` and could not be resampled; that class of bug is what the constants prevent).

| Constant | Value | Meaning | Written by |
|----------|-------|---------|------------|
| `META_ORIGIN` | `"origin"` | Provenance label of the producing feature | `from_dataframe(origin=...)` |
| `META_ORIGIN_PATH` | `"origin_path"` | Source file path of a raw table | raw loaders |
| `META_SAMPLE_INTERVAL` | `"sample_interval"` | Sampling interval (`pd.Timedelta`); presence marks a regular time series | `from_dataframe(sample_interval=...)`, `resample()` |
| `META_EXTENSION_NAME` | `"extension_name"` | Owning extension | `Dataset.add_raw_datatable` (automatic) |

> **`origin` vs `extension_name`.** Both record "where a table came from". `extension_name` is set
> automatically for **raw** tables (`raw_datatables[ext][name]`) and namespaces them; `origin` is a
> free provenance label you pass for **generated/derived** tables that live in `datatables`.

### Persistence caveat — keep metadata JSON-native

Metadata is persisted into a DuckDB `JSON` column and read back as `dict[str, Any]`
(`core/io/storage.py`). So:

- **Values must be JSON-native** (str/number/bool/list/dict). Anything else may fail to serialize or
  lose its type on round-trip.
- A `pd.Timedelta` stored under `sample_interval` comes back as a **`str`** after save/load. The
  `Datatable.sample_interval` property therefore re-normalizes its stored value through
  `pd.Timedelta(value)` (idempotent) so callers always get a `pd.Timedelta`. Do **not** read
  `metadata["sample_interval"]` directly — go through the property.

---

## Time-axis guards

Because generated tables may be cross-sectional, the time-based members guard on the presence of a
`DateTime` column (`is_timeseries`):

- **Accessors raise** — `start_timestamp`, `end_timestamp`, `duration` raise `ValueError` on a
  non-time-series table (a fabricated timestamp would be meaningless; callers that might touch a
  cross-sectional table already guard or catch).
- **Mutators no-op** — `exclude_time`, `trim_time`, `resample` return early on a non-time-series
  table. This matters because `Dataset.exclude_time` / `trim_time` / `resample` iterate **every**
  datatable (including any generated cross-sectional ones a user added), so a dataset-wide
  Trim/Exclude/Resample must skip tables that have no time axis instead of crashing.

Time-series tables are unaffected — the guards pass straight through.

---

## `clone()`

`Datatable.clone()` deep-copies the frame, variables, and metadata, **preserves
`outliers_settings`**, and assigns a **fresh `id`**. The fresh id is intentional: the persisted
DuckDB df-table name is keyed on `dataset.id + datatable.id`, so a duplicated id would collide
(`core/io/storage.py`). `Dataset.clone()` relies on this when copying tables into a new dataset.

---

## Registering the result

The builder returns a detached datatable. To make it part of the workspace, go through the
[service facade](03-services-manager.md) so the change is broadcast:

```python
from tse_analytics.core import manager

datatable = Datatable.from_dataframe(dataset, name, df, origin="MyTool")
manager.add_datatable(datatable)  # -> dataset.datatables[name]; broadcasts WorkspaceChangedMessage
```

`manager.add_datatable` keys the table by `name` in `dataset.datatables` (a duplicate name
overwrites — generation sites append a timestamp to keep names unique). Raw importer tables instead
use `Dataset.add_raw_datatable(extension_name, datatable)`, which sets `META_EXTENSION_NAME` and
stores them under `raw_datatables[extension_name][name]`. → [10-modules-extensions.md](10-modules-extensions.md)

---

## Recipe — emit a result table from a toolbox widget

1. Compute a result `DataFrame` with an identifier column (`"Animal"` for per-animal results, or the
   group-by factor name for per-group summaries).
2. Build the datatable: `Datatable.from_dataframe(self.datatable.dataset, name, df, origin="MyTool")`
   — add `sample_interval=` if it is a regular time series, or `variables={...}` for full control.
3. Register it: `manager.add_datatable(datatable)`.

See `toolbox/chronobiology/chronobiology_widget.py` (`_add_datatable`) for a complete, working
"Add Datatables" implementation.

---

**Next:** [← Back to the index](README.md)
