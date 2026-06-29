# Contributing to TSE Analytics

Thank you for your interest in contributing to **TSE Analytics** — the desktop application for
analyzing TSE PhenoMaster, IntelliCage, and IntelliMaze experimental data. This guide covers the
development setup, project layout, code style, and workflow. For an overview of what the
application does, see the [README](README.md).

---

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Code Style & Quality](#code-style--quality)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Git Workflow](#git-workflow)
- [Dependency Management](#dependency-management)
- [Building & Deployment](#building--deployment)
- [Getting Help](#getting-help)
- [License](#license)

---

## Development Setup

### Prerequisites

- **Python 3.14.5** — the exact version pinned in `pyproject.toml` (`requires-python = "==3.14.5"`).
- **[uv](https://docs.astral.sh/uv/)** — package & environment manager.
- **[Task](https://taskfile.dev/)** — task runner used for all build/test commands.
- **Git** — version control.

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/TSE-Systems/tse-analytics.git
cd tse-analytics

# 2. Create the environment and install dependencies
uv sync

# 3. Verify the installation by running the test suite
task test
```

---

## Project Structure

```
tse-analytics/
├── tse_analytics/          # Main source code
│   ├── core/               # Domain models, messaging, services, workers, io, layouts, utils
│   ├── modules/            # Self-contained data-source modules (phenomaster, intellicage, intellimaze)
│   ├── toolbox/            # Analysis widgets (histogram, ANOVA, PCA, regression, …)
│   ├── pipeline/           # Node-based visual data processing (NodeGraphQt)
│   ├── views/              # Shared UI components, dialogs, and the main window
│   └── styles/             # SCSS source → compiled QSS stylesheets
├── tests/                  # pytest suite (mirrors the source structure)
├── docs/                   # Documentation
│   ├── user/               # Generated end-user documentation site
│   └── dev/                # Developer reference (architecture, subsystems, extending cookbook)
├── resources/              # Application resources (icons, images, .qrc)
├── packaging/              # Installation/deployment configs (PyInstaller spec, Inno Setup, Flatpak)
├── pyproject.toml          # Project configuration & dependencies
├── Taskfile.yml            # Task runner definitions
└── .editorconfig           # Editor configuration
```

### Important notes

- **Do NOT commit auto-generated files.** Files ending in `*_ui.py` (compiled from Qt Designer
  `.ui` files) and `*_rc.py` (compiled from `.qrc` resource files) are excluded from version
  control. Rebuild them with `task build-ui` / `task build-resources` after editing the sources.
- **Modules are self-contained.** Each module (`phenomaster`, `intellicage`, `intellimaze`) bundles
  its own data, views, io, and models.

---

## Documentation

- **Developer reference** — architecture diagrams, subsystem walkthroughs, the full
  toolbox/pipeline catalog, and an extending cookbook: [`docs/dev/`](docs/dev/README.md)
  (`docs/dev/README.md` is the index).
- **Canonical conventions** — the auto-loaded rules under `.claude/rules/`: `code-style.md`,
  `commands.md`, `project-structure.md`, `testing.md`, `toolbox-widget-pattern.md`. The project
  overview for AI/contributor tooling lives in [`.claude/CLAUDE.md`](.claude/CLAUDE.md).
- **End-user documentation** — the generated site under [`docs/user/`](docs/user/).

---

## Code Style & Quality

### Formatting

The project uses **[Ruff](https://docs.astral.sh/ruff/)** for both linting and formatting:

- **Line length:** 120 characters
- **Target version:** Python 3.14 (`py314`)
- **Docstring convention:** Google style
- **Indentation / endings / encoding:** 4 spaces, LF, UTF-8 (configured in `.editorconfig`)

### Type checking

The project runs **two** static type checkers — both should pass:

- **[pyrefly](https://pypi.org/project/pyrefly/)** — `task pyrefly`
- **[ty](https://pypi.org/project/ty/)** — `task ty`

(There is no `mypy` task; the legacy `[tool.mypy]` block in `pyproject.toml` is not part of the
standard workflow.)

### Quality commands

```bash
task ruff-format   # format code
task ruff-check    # lint
task ruff-fix      # auto-fix lint issues
task pyrefly       # type check (pyrefly)
task ty            # type check (ty)
task test          # run the test suite
task coverage      # run tests with coverage
```

### Conventions

1. **Imports** — standard library → third-party → local (`tse_analytics.*`); sorted by isort
   (via Ruff). Use absolute imports.
2. **Naming** — `PascalCase` classes, `snake_case` functions/methods, `UPPER_SNAKE_CASE`
   constants, `_prefix` for private members.
3. **Docstrings** — Google style; document public classes, methods, and functions with
   `Args` / `Returns` / `Raises` sections where applicable.
4. **Type hints** — modern Python 3.14 syntax (`list[str]`, `dict[str, int]`, `X | None`).
5. **Logging** — use `loguru`, not the stdlib `logging`: `from loguru import logger`.
6. **pandas dtypes** — always use numpy-nullable dtypes (`Int64`, `Float64`, `string`, …); data is
   normalized in `tse_analytics/core/utils/data.py`.

### Example

```python
from pathlib import Path
from typing import Any

from loguru import logger


class DataProcessor:
    """Processes experimental data from TSE PhenoMaster.

    This class handles data loading, validation, and preprocessing
    for various experimental setups.

    Attributes:
        data_path: Path to the data directory.
        cache_enabled: Whether to cache processed results.
    """

    def __init__(self, data_path: Path, cache_enabled: bool = True) -> None:
        """Initialize the data processor.

        Args:
            data_path: Path to the data directory.
            cache_enabled: Whether to enable result caching.
        """
        self.data_path = data_path
        self.cache_enabled = cache_enabled
        logger.debug(f"DataProcessor initialized with path: {data_path}")

    def process_dataset(self, dataset_id: str) -> dict[str, Any]:
        """Process a single dataset.

        Args:
            dataset_id: Unique identifier for the dataset.

        Returns:
            Dictionary containing processed data and metadata.

        Raises:
            ValueError: If dataset_id is invalid.
        """
        if not dataset_id:
            raise ValueError("Dataset ID cannot be empty")

        logger.info(f"Processing dataset: {dataset_id}")
        # Implementation here
        return {}
```

---

## Development Workflow

### Working with PySide6 UI files

UI files are designed in Qt Designer (`.ui`) and must be compiled to Python after editing:

```bash
# Build all UI files
task build-ui

# Build a specific group of UI files
task build-ui:views
task build-ui:toolbox
task build-ui:phenomaster
task build-ui:intellicage
task build-ui:intellimaze
```

### Building resources

After modifying resources (icons, images, …):

```bash
task build-resources
```

### Building stylesheets

After modifying the SCSS sources under `tse_analytics/styles/scss`:

```bash
task qss
```

### Running the application

```bash
uv run tse-analytics
```

### Extending the app

The developer docs include a full cookbook in
[`docs/dev/12-extending.md`](docs/dev/12-extending.md); the short version:

- **Add a toolbox analysis widget** — subclass `ToolboxWidgetBase`
  (`tse_analytics/toolbox/toolbox_widget_base.py`), register it with the `@toolbox_plugin`
  decorator, and add an import in `tse_analytics/toolbox/__init__.py` so the decorator runs at
  startup. See `.claude/rules/toolbox-widget-pattern.md`.
- **Add a pipeline node** — subclass `PipelineNode` (`tse_analytics/pipeline/pipeline_node.py`),
  implement `process(packet)`, and register it in
  `tse_analytics/views/pipeline/pipeline_editor_widget.py`.
- **Add a module extension** — create `modules/<module>/extensions/<ext>/` and register the
  raw-table → widget mapping in that module's `extensions/extensions_registry.py`.

---

## Testing

- **Framework:** [pytest](https://docs.pytest.org/).
- **Location:** tests live in `tests/` and mirror the source structure.
- **Fixtures:** shared fixtures live in `conftest.py` files.

```bash
# Run all tests
task test

# Run tests with coverage
task coverage

# Run a single test file
uv run pytest tests/test_specific.py
```

Aim for meaningful coverage, follow pytest conventions, and mock external dependencies where
appropriate.

---

## Git Workflow

### Branching

- `main` — stable production code.
- Feature branches — `feature/description`.
- Bug fixes — `bugfix/description`.
- Releases — `release/version`.

### Commit messages

Write clear, descriptive messages:

```
Short summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain what changed and why, not how.

- Use the present tense ("Add feature", not "Added feature")
- Reference issues/PRs where applicable
```

### Before committing

```bash
task ruff-format   # format
task ruff-check    # lint
task pyrefly       # type check
task ty            # type check
task test          # run tests
task build-ui      # only if you edited .ui files
```

### Pull request guidelines

1. **Title** — clear and descriptive.
2. **Description** — explain what changed and why.
3. **Testing** — describe how you verified the change.
4. **Screenshots** — include them for UI changes.
5. **Checklist:**
   - [ ] Code follows the style guidelines
   - [ ] Tests added/updated
   - [ ] Documentation updated if needed
   - [ ] All tests pass
   - [ ] No linting or type-checking errors
   - [ ] No generated `*_ui.py` / `*_rc.py` files committed

---

## Dependency Management

### Adding dependencies

1. Add the package to `pyproject.toml` under `dependencies` (runtime) or
   `dependency-groups.dev` (development).
2. Run `uv sync` to install.
3. Commit both `pyproject.toml` and `uv.lock`.

### Updating dependencies

```bash
# Update uv, lockfile, and environment
task update

# Update a specific package
uv add package@latest
```

---

## Building & Deployment

```bash
# Standalone build with PyInstaller
task deploy

# Build with PySide6 deployment
task deploy-pyside

# Remove build, test, and coverage artifacts
task clean
```

---

## Getting Help

- **Issues** — report bugs and request features on
  [GitHub Issues](https://github.com/TSE-Systems/tse-analytics/issues).
- **Developer questions** — start with the developer reference in [`docs/dev/`](docs/dev/README.md)
  and the conventions under `.claude/rules/`.
- **End-user documentation** — see the generated site under [`docs/user/`](docs/user/).

---

## License

By contributing to TSE Analytics, you agree that your contributions will be licensed under the
**GNU General Public License v3.0 or later** (GPL-3.0-or-later). See [LICENSE](LICENSE) for the
full text.
