# 08 — Toolbox

[← Back to index](README.md)

The **toolbox** is the collection of analysis/visualization widgets the user opens against a
`Datatable`. Every widget shares one base class and is discovered through a decorator-based plugin
registry. This document covers that infrastructure and then catalogs every widget.

**Source:** `tse_analytics/toolbox/` (plus IntelliCage-specific widgets under
`tse_analytics/modules/intellicage/toolbox/`).

---

## `ToolboxWidgetBase`

**Source:** `toolbox/toolbox_widget_base.py`

Most toolbox widgets subclass `ToolboxWidgetBase` (a `QWidget`). The base provides the common shell
so each widget only implements its own logic. (The registry's real requirement is structural — see
[Plugin registry & discovery](#plugin-registry--discovery) — so a few data-viewer widgets satisfy it
directly on `QWidget` instead.)

```python
class ToolboxWidgetBase(QWidget):
    title: str = ""

    def __init__(self, datatable, settings_type, title=None, parent=None): ...
```

What the base sets up automatically:

- A **toolbar** with an **Update** action (calls `_update`), a separator, the subclass's custom
  items, a spacer, and an **Add Report** action.
- A **`ReportEdit`** HTML view (`self.report_view`) filling the body — analyses render HTML into it.
- **Settings persistence** via `QSettings`, keyed by the widget's class name. On construction it
  loads the saved settings dataclass (falling back to a default instance); on destruction it saves
  `self._get_settings_value()`.
- **Add Report** prompts for a name and calls `manager.add_report(Report(dataset, name,
  report_view.toHtml()))` (see [03-services-manager.md](03-services-manager.md)).
- `self.datatable` (the `Datatable` being analyzed) and `self.toast` (a pyqttoast handle).

### The subclass contract

| Method | Required? | Purpose |
|--------|-----------|---------|
| `_create_toolbar_items(self, toolbar)` | Optional | Add selectors/spinboxes/labels to the toolbar. Called during `__init__` after the Update button. |
| `_get_settings_value(self) -> Any` | **Required** | Return the current settings dataclass instance to persist. |
| `_update(self) -> None` | **Required** | Run the analysis and render HTML into `self.report_view`. Bound to the Update button. |

Plus set `title` (class attribute or constructor arg). Long-running `_update` work is offloaded to a
[`Worker`](04-threading-workers.md) and surfaced with a toast.

### Minimal skeleton

```python
from dataclasses import dataclass
from tse_analytics.toolbox.toolbox_registry import toolbox_plugin
from tse_analytics.toolbox.toolbox_widget_base import ToolboxWidgetBase


@dataclass
class MyToolSettings:
    variable: str = ""


@toolbox_plugin(category="Exploration", label="My Tool", icon=":/icons/exploration.png", order=99)
class MyToolWidget(ToolboxWidgetBase):
    title = "My Tool"

    def __init__(self, datatable, parent=None):
        super().__init__(datatable, MyToolSettings, parent=parent)
        self._build_controls()

    def _create_toolbar_items(self, toolbar):
        ...  # add variable selector etc.

    def _get_settings_value(self):
        return MyToolSettings(variable=self._variable_selector.currentText())

    def _update(self):
        df = self.datatable.get_filtered_df([...])
        html = run_analysis(df, self._settings)
        self.report_view.setHtml(html)
```

A full walkthrough (including the matching pipeline node) is in [12-extending.md](12-extending.md).

---

## Plugin registry & discovery

**Source:** `toolbox/toolbox_registry.py`, discovery driven by `toolbox/__init__.py`.

Widgets register themselves with the `@toolbox_plugin` class decorator:

```python
@toolbox_plugin(category="Exploration", label="Histogram", icon=":/icons/exploration.png", order=0)
class HistogramWidget(ToolboxWidgetBase): ...
```

- Each registration stores a frozen `ToolboxPluginInfo(category, label, icon, widget_class, order)`
  in the module-level `registry` singleton. Four **optional** fields carry declarative applicability:
  `dataset_types` (dataset types the tool applies to, `None` = any), `required_datatable_name` (a
  datatable the tool needs, e.g. `"Visits"`), `internal` (gated behind developer/internal features,
  e.g. the AI menu), and `tooltip`. `ToolboxPluginInfo.is_applicable(dataset, datatable)` evaluates
  the first two. The matching keyword-only decorator args default to the historical behavior (applies
  everywhere, non-internal), so existing decorations are unaffected.
- **The widget contract is structural, not `ToolboxWidgetBase`.** The registry only requires a class
  constructable as `widget_class(datatable)`; a `title` attribute is optional (the menu falls back to
  the plugin label). This is documented by the `ToolboxWidget` `typing.Protocol` in
  `toolbox_registry.py`. Most widgets get this for free from `ToolboxWidgetBase`, but the four
  **Data** widgets (`DataTableWidget`, `DataPlotWidget`, `FactorsPlotWidget`, `FastLinePlotWidget`)
  satisfy it directly on `QWidget`.
- **Discovery:** `toolbox/__init__.py` imports every widget module (and the IntelliCage toolbox
  widgets) so their decorators run at startup, populating the registry **before** menus are built.
  If you add a widget, add its import here or it won't appear —
  `tests/toolbox/test_toolbox_registry.py` is a drift guard that fails if a decorated widget is
  missing from the manifest (and also checks duplicate labels, unique `order` per category, and the
  structural contract). `validate_registry()` logs the cheap subset (duplicate labels / empty icons)
  at startup.
- `ToolboxButton` (`views/misc/toolbox_button.py`) reads `registry.get_plugins()` to build the
  categorized "add analysis" menu. Categories follow `CATEGORY_ORDER`; widgets within a category are
  sorted by `order`. Menu/action visibility is computed generically from each plugin's metadata
  (`is_applicable()` + `internal`) in `_refresh_visibility()` — there is no per-tool string-matching.

**`CATEGORY_ORDER`:**
`AI` · `Data` · `Exploration` · `Bivariate` · `ANOVA` · `Factor Analysis` · `Chronobiology` ·
`Time Series` · `IntelliCage` (any unlisted category is appended alphabetically).

### Companion files in a widget package

A typical widget folder (`toolbox/<tool>/`) contains:

- `<tool>_widget.py` — the `ToolboxWidgetBase` subclass (UI + orchestration).
- `processor.py` — **pure computation** (takes a DataFrame + settings, returns results/figures).
  Keeping compute here makes it reusable from both the widget and the pipeline node, and easy to
  unit-test.
- `<tool>_node.py` — an optional [pipeline node](09-pipeline.md) wrapping the same `processor`.
- `*_settings_widget.ui` / `*_settings_widget_ui.py` — for widgets with a richer settings dialog
  (the ANOVA family, Place Preference).

---

## Widget catalog

Grouped by category. "Node" = a matching `*_node.py` exists; "**registered**" = it is also wired
into the pipeline editor (`views/pipeline/pipeline_editor_widget.py`). Where a node file exists but
is not wired into the editor, that is noted explicitly.

### AI
| Widget | What it does | Files |
|--------|--------------|-------|
| **TSE Assistant** | Natural-language data assistant. Backed by Anthropic Claude (`claude.py`) or a local LMStudio model (`lmstudio.py`); a prompt is built from the datatable (`prompt_builder.py`) so the user can ask questions in plain English. | `toolbox/ai_agent/` |

### Data
| Widget | What it does | Files | Node |
|--------|--------------|-------|------|
| **Table** | Interactive DataFrame viewer: column selection, sort, export (CSV/Excel), descriptive stats, NA handling. | `toolbox/data_table/` | — |
| **Fast Line Plot** | High-performance pyqtgraph line/scatter plot with detail+overview range slider; per-animal filtering. | `toolbox/fast_line_plot/` | — |
| **Facet Plot** | Seaborn facet grid of bar plots with error bars (one subplot per facet level). | `toolbox/facet_data_plot/` | — |
| **Line Plot** | Seaborn multi-variable line plot with mean ± error band, group coloring, light/dark shading. | `toolbox/data_plot/` | Node (**registered**) |

### Exploration
| Widget | What it does | Files | Node |
|--------|--------------|-------|------|
| **Histogram** | Distribution histogram with group coloring. | `toolbox/histogram/` | Node (**registered**) |
| **Distribution** | Violin / box / raincloud plots with optional point overlay. | `toolbox/distribution/` | Node (**registered**) |
| **Normality** | Normality tests (Shapiro–Wilk, etc.) with Q–Q plots, per group. | `toolbox/normality/` | — |
| **Composite Performance Score** | Weighted, normalized (Z-score / min–max) multi-variable score with per-direction weighting; bar plot by group. | `toolbox/composite_score/` | — |

### Bivariate
| Widget | What it does | Files | Node |
|--------|--------------|-------|------|
| **Correlation** | Scatter + regression line + CI; Pearson/Spearman r and p, per group. | `toolbox/correlation/` | Node (**registered**) |
| **Regression** | Linear regression of response on covariate, per group, with residual diagnostics. | `toolbox/regression/` | Node (**registered**) |

### ANOVA
| Widget | What it does | Files | Node |
|--------|--------------|-------|------|
| **One-way ANOVA** | Single between-subject factor; selectable effect size. | `toolbox/one_way_anova/` | Node (**registered**) |
| **N-way ANOVA** | ≥2 between-subject factors; main effects + interactions; p-adjustment. | `toolbox/n_way_anova/` | Node (**registered**) |
| **Repeated Measures ANOVA** | 1–2 within-subject factors; optional pairwise post-hoc. | `toolbox/rm_anova/` | Node (**registered**) |
| **Mixed-design ANOVA** | Between × within factors with interaction. | `toolbox/mixed_anova/` | Node (**registered**) |
| **ANCOVA** | One between-subject factor with a continuous covariate. | `toolbox/ancova/` | Node (**registered**) |

(The ANOVA family uses `*_settings_widget.ui` dialogs for factor/effect-size/p-adjust selection.)

### Factor Analysis
| Widget | What it does | Files | Node |
|--------|--------------|-------|------|
| **Correlation Matrix** | Heatmap of pairwise correlations over selected variables. | `toolbox/correlation_matrix/` | Node (**registered**) |
| **Matrix Plot** | Seaborn pairplot (scatter/kde/hist) with group coloring. | `toolbox/matrix_plot/` | Node (**registered**) |
| **PCA** | Principal component analysis: scree plot, biplot, loadings, group coloring. | `toolbox/pca/` (+ `plots.py`) | Node (**registered**) |
| **t-SNE** | t-distributed stochastic neighbor embedding (2D/3D), configurable perplexity/metric. | `toolbox/tsne/` | Node (**registered**) |
| **MDS** | Multidimensional scaling, configurable distance metric, 2D/3D. | `toolbox/mds/` | Node (**registered**) |
| **UMAP** | UMAP manifold projection, configurable neighbors/min_dist/metric. | `toolbox/umap/` | Node (**registered**) |

### Chronobiology
| Widget | What it does | Files | Node |
|--------|--------------|-------|------|
| **Chronobiology** | Circadian rhythmicity: onset/offset detection, period & harmonic parameters. | `toolbox/chronobiology/` | — |
| **Actogram** | Double-plotted actogram per animal for visualizing activity patterns. | `toolbox/actogram/` | Node (**registered**) |
| **Periodogram** | Lomb–Scargle periodogram for period detection over a configurable range. | `toolbox/periodogram/` | — |

### Time Series
| Widget | What it does | Files | Node |
|--------|--------------|-------|------|
| **Decomposition** | Trend/seasonal/residual decomposition (naive additive/multiplicative or STL), per animal. | `toolbox/timeseries_decomposition/` | — |
| **Autocorrelation** | ACF / PACF plots for a single animal. | `toolbox/timeseries_autocorrelation/` | — |

### IntelliCage
These ship under `modules/intellicage/toolbox/` (registered in the toolbox the same way, with
category `IntelliCage`), because they operate on IntelliCage-specific tables. Their decorators
declare `dataset_types=("IntelliCage", "IntelliMaze")` (and Transitions / Place Preference also
`required_datatable_name="Visits"`), so the menu only offers them for the matching selection.

| Widget | What it does | Files |
|--------|--------------|-------|
| **Transitions** | Corner-transition (Markov) analysis with significance testing; transition heatmaps. | `modules/intellicage/toolbox/transitions/` |
| **Place Preference** | Corner-visit preference; filter by visit condition / nosepoke / lick; counts, normalized counts, durations. | `modules/intellicage/toolbox/place_preference/` |
| **Learning Curve** | Learning progression (correct visits, place/nosepoke error rate, licks per visit); bin by time or visit count; Excel export. | `modules/intellicage/toolbox/learning_curve/` |

---

## Reports

A small `toolbox/report/` package provides the report widget/node used to collect HTML output into
dataset `Report`s. Every toolbox widget's **Add Report** button funnels into the same
`manager.add_report(...)` path, and reports persist with the workspace
(see [06-persistence.md](06-persistence.md)).

---

**Next:** [09 — Pipeline →](09-pipeline.md)
