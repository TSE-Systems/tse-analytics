# CLAUDE.md

TSE Analytics — PySide6 desktop app for analyzing TSE PhenoMaster, IntelliCage and IntelliMaze experimental data.

## Quick Start

- Python version must be 3.14 (pinned to `==3.14.5` in `pyproject.toml`).
- Use `uv` for environment and dependencies: `uv sync`.
- Task runner is `task` (see `Taskfile.yml` and `.claude/rules/commands.md`).
- Run the app: `uv run tse-analytics`.
- UI is built with PySide6; docking via `pyside6-qtads`.
- Data analysis pipeline editor is based on the NodeGraphQt library.
- With Pandas always use numpy-nullable data types (`Int64`, `Float64`, `string`, …).

## Developer Documentation

For deeper reference than these rules — architecture diagrams, subsystem walkthroughs, the full
toolbox/pipeline-node catalogs, and an extending cookbook — see the developer docs in `dev-docs/`
(`dev-docs/README.md` is the index). They expand on this file and `.claude/rules/` with rationale
and detail; they are **not** auto-loaded, so consult them when the canonical rules aren't enough.

Map: `01-architecture`, `02-messaging`, `03-services-manager`, `04-threading-workers`,
`05-data-model`, `06-persistence`, `07-layouts-ui`, `08-toolbox`, `09-pipeline`,
`10-modules-extensions`, `11-conventions`, `12-extending`.

## Architecture

Package layout under `tse_analytics/`:

- `core/` — domain models (`data/`, `models/`), persistence (`io/`), `messaging/`, `services/`,
  `workers/`, `layouts/`, `utils/`. Service facade in `core/manager.py`.
- `modules/` — self-contained data-source modules: `phenomaster`, `intellicage`, `intellimaze`.
- `toolbox/` — analysis widgets (histogram, ANOVA, PCA, regression, AI agent, facet plots, …).
- `pipeline/` — node-based visual data processing (NodeGraphQt).
- `views/` — shared UI components, dialogs, and the main window.
- `styles/` — SCSS source compiled to QSS. `resources/` — icons/images compiled to `*_rc.py`.

### Bootstrap

`tse_analytics/main.py` defines `App(QApplication)` (Fusion light theme, QSS loaded from
`styles/qss/`, `TaskManager` singleton init) and launches `MainWindow(sys.argv)`
(`views/main_window.py`). The docking layout is managed by `LayoutManager`
(`core/layouts/layout_manager.py`), which wraps `pyside6-qtads`.

### Messaging backbone

Widgets and services communicate through a pub/sub messenger — this is the central decoupling
pattern; learn it before adding UI.

```python
from tse_analytics.core import messaging

messaging.subscribe(self, messaging.DatasetChangedMessage, self._on_dataset_changed)
messaging.broadcast(messaging.DatasetChangedMessage(self, dataset))
```

- UI components that react to app state extend `MessengerListener`.
- Key messages: `DatasetChangedMessage`, `DatatableChangedMessage`, `WorkspaceChangedMessage`,
  `DataChangedMessage`, `SelectedTreeItemChangedMessage`, `AddToReportMessage`,
  `OutliersChangedMessage`, `ReportsChangedMessage`.
- Implementation: `core/messaging/{messenger,messages,messenger_listener}.py`; public API and the
  singleton messenger are exposed from `core/messaging/__init__.py`.

### Service facade

`core/manager.py` wires the four singleton services from `core/services/`
(`selection_service`, `workspace_service`, `dataset_service`, `importer_service`) and re-exports
their methods as module-level functions. **Call `manager.*` (e.g. `manager.add_dataset(...)`,
`manager.set_selected_dataset(...)`) — do not instantiate services yourself.** Services broadcast
messages on state changes.

### Threading

For long-running work, wrap it in a `Worker` (`core/workers/worker.py`, a `QRunnable` emitting
`result` / `error` / `finished` via `worker_signals.py`) and submit it through
`TaskManager.start_task(worker)` (`core/workers/task_manager.py`). Never block the UI thread.

## Domain Model

Ownership hierarchy (`core/data/`):

```
Workspace (workspace.py)
└── Dataset (dataset.py)
    ├── datatables: dict[str, Datatable]
    ├── raw_datatables: dict[str, dict[str, Datatable]]   # extension-namespaced
    ├── animals, factors, reports
```

Shared value types (`Animal`, `Factor`, `Variable`, levels) live in `core/data/shared.py`;
`Report` in `core/data/report.py`.

- **Datatable** (`core/data/datatable.py`) wraps a pandas `DataFrame` (`.df`) using
  numpy-nullable dtypes (normalized in `core/utils/data.py`). Standard columns: `Animal`,
  `DateTime`, `Timedelta`. Carries `variables` (column metadata) and `outliers_settings`.
- **Factors / binning** are applied via `core/data/factor_appliers.py` (time intervals,
  light/dark cycles, named time phases, by-animal, by-animal-property, by-column). Built-in
  default factors (`Animal`, `Total`, `LightCycle`) are built in
  `core/data/dafault_factor_builders.py` (filename spelling is intentional in-repo).
- **Terminology**: the experiment-run concept is called **"Experiment"** (renamed from "Run").
  Use `experiment_*` vocabulary; no `Run` class remains.
- **Persistence**: workspaces save to DuckDB `.duckdb` files (data tables plus `_meta_*`
  metadata tables), with legacy pickle `.workspace` support — `core/io/storage.py`,
  `core/services/workspace_service.py`.

## Extending the App

### Add a toolbox analysis widget

Subclass `ToolboxWidgetBase` (`toolbox/toolbox_widget_base.py`) and register with the
`@toolbox_plugin` decorator (`toolbox/toolbox_registry.py`), then add an import in
`toolbox/__init__.py` so the decorator runs at startup.

```python
@toolbox_plugin(category="Exploration", label="Histogram", icon=":/icons/...", order=0)
class HistogramWidget(ToolboxWidgetBase): ...
```

Categories (`CATEGORY_ORDER`): AI, Data, Exploration, Bivariate, ANOVA, Factor Analysis,
Chronobiology, Time Series, IntelliCage. Full method contract:
`.claude/rules/toolbox-widget-pattern.md`.

Module-specific widgets may instead live under `modules/<module>/toolbox/` (e.g. IntelliCage's
`learning_curve`, `place_preference`, `transitions`); they are registered the same way — by adding
their import to `toolbox/__init__.py`.

### Add a pipeline node

Subclass `PipelineNode` (`pipeline/pipeline_node.py`), implement
`process(packet) -> PipelinePacket | dict[str, PipelinePacket]` (`pipeline/pipeline_packet.py`),
and register it in `views/pipeline/pipeline_editor_widget.py`. Most toolbox widgets ship a
matching `*_node.py` variant.

### Add a module extension

For `phenomaster` / `intellimaze`, create `modules/<module>/extensions/<ext>/`
(views / data / io / processor / settings) and register the raw-table → widget mapping in that
module's `extensions/extensions_registry.py`.

## Plan persistence

After completing implementation of a plan (whether produced via Plan Mode or
ad-hoc), save the final plan to `./.claude/plans/` in this project as a Markdown file.

- Filename format: `YYYY-MM-DD-<kebab-case-summary>.md`
- Include: the original task statement, the executed plan, files touched,
  and any follow-ups or known limitations.
- Do this before ending the turn that completes the implementation.
- Never write plans to `~/.claude/plans/` for this project — always use
  `./.claude/plans/` so the plan is committed alongside the code.

## Generated Files — Do Not Edit or Commit

- `*_ui.py` — generated from `.ui` files via `pyside6-uic`
- `*_rc.py` — generated from `.qrc` files via `pyside6-rcc`

After editing `.ui` files run `task build-ui`. After editing resources run `task build-resources`. After editing SCSS
run `task qss`.

## Dependencies

- Add deps in `pyproject.toml` under `dependencies` or `dependency-groups.dev`
- Run `uv sync` to install; commit both `pyproject.toml` and `uv.lock`
- Update all: `task update`

## Conventions

Detailed rules live in `.claude/rules/` (auto-loaded — don't duplicate them here):
`code-style.md`, `commands.md`, `project-structure.md`, `testing.md`, `toolbox-widget-pattern.md`.
The expanded developer reference (rationale, diagrams, full catalogs) lives in `dev-docs/` — see the
[Developer Documentation](#developer-documentation) section above.
