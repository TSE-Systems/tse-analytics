# 11 — Conventions, tooling & rules

[← Back to index](README.md)

This document distills the project's coding standards, build commands, and house rules. The
canonical, always-loaded version lives in `.claude/CLAUDE.md`; this is the explained companion.

---

## Environment

- **Python:** pinned to `==3.14.6` (`pyproject.toml`, `requires-python`).
- **Package manager:** [`uv`](https://docs.astral.sh/uv/). Install/sync deps with `uv sync`. Run
  the app with `uv run tse-analytics`.
- **Task runner:** [`task`](https://taskfile.dev/) — see `Taskfile.yml`.

---

## Code style

Enforced by **Ruff** (config in `pyproject.toml`):

- **Line length 120**, target **py3.14**, `preview = true`.
- Lint rule sets: `E`, `W` (pycodestyle), `F` (pyflakes), `I` (isort), `B` (bugbear),
  `C4` (comprehensions), `UP` (pyupgrade), `NPY201` (numpy-2 deprecations). `E501` and `F821` are
  ignored.
- **Docstrings:** Google convention (`pydocstyle`).
- **Type hints:** modern syntax — `list[str]`, `dict[str, int]`, `X | None`.
- **Logging:** `from loguru import logger` — **not** the stdlib `logging` module.
- **Naming:** `PascalCase` classes, `snake_case` functions, `UPPER_SNAKE_CASE` constants,
  `_prefix` for private members.
- **Imports:** stdlib → third-party → local (`tse_analytics.*`), sorted by isort (via Ruff).

Type checking is available via two checkers (both non-blocking in CI tasks): **pyrefly** and **ty**.

### pandas dtype rule

Always use **numpy-nullable** dtypes (`Int64`, `Float64`, `string`, `boolean`, …) rather than the
classic numpy dtypes. The domain model normalizes to these (`core/utils/data.py`); new columns and
computations should stay consistent so persistence round-trips cleanly
([06-persistence.md](06-persistence.md)).

---

## Commands (`Taskfile.yml`)

| Command | What it does |
|---------|--------------|
| `task test` | Run the pytest suite (`pytest tests/`) |
| `task coverage` | Run tests with coverage |
| `task ruff-format` | Format code (`ruff format .`) |
| `task ruff-check` | Lint (`ruff check .`) |
| `task ruff-fix` | Auto-fix lint issues (`ruff check . --fix`) |
| `task pyrefly` | Type-check with pyrefly |
| `task ty` | Type-check with ty |
| `task build-ui` | Compile **all** `.ui` → `*_ui.py` (per-area subtasks: views/toolbox/phenomaster/intellicage/intellimaze) |
| `task build-resources` | Compile `resources/resources.qrc` → `tse_analytics/resources_rc.py` |
| `task qss` | Compile `styles/scss` → `styles/qss` (qtsass) |
| `task deploy` | `uv sync` + PyInstaller build (`packaging/tse-analytics.spec`) |
| `task deploy-pyside` | `pyside6-deploy` build (`pysidedeploy.spec`) |
| `task flatpak-dist` | Build the PyInstaller bundle inside a manylinux container (portable) |
| `task flatpak` | Build & install the Flatpak locally (Linux) |
| `task flatpak-bundle` | Build a single-file `.flatpak` for distribution |
| `task update` | Update uv + upgrade lockfile + sync |
| `task clean` | Remove build/test artifacts and generated `*_ui.py` / `*_rc.py` |
| `uv run tse-analytics` | Run the app in development |

The deploy/flatpak tasks are explained in full — including the two-stage manylinux Flatpak
build — in [13-packaging-deployment.md](13-packaging-deployment.md).

---

## Generated files — do not hand-edit or hand-commit as source

These are compiled outputs. Edit the **source**, then run the build task:

| Generated | Source | Rebuild with |
|-----------|--------|--------------|
| `*_ui.py` | `.ui` (Qt Designer) | `task build-ui` |
| `*_rc.py` (`resources_rc.py`) | `.qrc` (`resources/resources.qrc`) | `task build-resources` |
| `styles/qss/*.css` | `styles/scss/*.scss` | `task qss` |

Ruff/pylint/mypy/pyrefly are all configured to **exclude** `*_ui.py` (and `*_rc.py`).

---

## Dependencies

- Declare runtime deps in `pyproject.toml` under `[project] dependencies`; dev tools under
  `[dependency-groups] dev`. Versions are pinned exactly (`==`).
- After changing deps, run `uv sync` and **commit both `pyproject.toml` and `uv.lock`**.
- Bump everything with `task update`.

Notable runtime libraries: PySide6 + `pyside6-qtads` + `nodegraphqt` (UI), `pandas` + `duckdb`
(data), `scipy` / `statsmodels` / `scikit-learn` / `pingouin` / `umap-learn` / `astropy` / `lmfit`
(stats & ML), `matplotlib` / `seaborn` / `pyqtgraph` / `ptitprince` / `great-tables` (viz/report),
`anthropic` + `lmstudio` (the AI assistant), `traja` (trajectory analysis), `loguru` (logging),
`psutil` (memory readout).

---

## Testing

- Framework: **pytest**; tests live in `tests/`, mirroring the source tree
  (`tests/core/...`, `tests/toolbox/...`, `tests/modules/...`, `tests/views/...`).
- Shared fixtures in `conftest.py` files.
- The most thorough coverage is around the **`processor.py`** modules (pure compute is easy to
  test): e.g. `tests/toolbox/actogram/test_processor.py`,
  `tests/modules/intellicage/toolbox/test_learning_curve_processor.py`, plus core data tests
  (`test_dataset.py`, `test_datatable.py`, `test_factor_appliers.py`, `test_outliers.py`) and
  worker tests (`test_worker.py`, `test_task_manager.py`).
- This is a strong reason to keep computation in `processor.py` rather than inside widgets: it can
  be unit-tested without a Qt event loop. Run with `task test`.

---

## Settings (`QSettings`)

UI/runtime preferences persist via `QSettings`, keyed by the organization/application identity set
in `App.__init__` (see [01-architecture.md](01-architecture.md)). Examples: selected theme
(`appStyle`, default `tse-light`), window geometry and dock state, recent-files list, and figure
DPI/size. Each toolbox widget also persists its settings dataclass under its class name
([08-toolbox.md](08-toolbox.md)).

---

## Plan persistence rule

After completing an implementation task (Plan Mode or ad-hoc), save the final plan to
`./.claude/plans/` **in this repo** (not `~/.claude/plans/`) as
`YYYY-MM-DD-<kebab-case-summary>.md`, including the task statement, executed plan, files touched,
and follow-ups. This keeps the plan committed alongside the code.

---

**Next:** [12 — Extending the app →](12-extending.md)
