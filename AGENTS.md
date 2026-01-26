# TSE Analytics Agent Notes

This repository contains the TSE Analytics desktop application (PySide6) for analyzing
PhenoMaster, IntelliCage, and IntelliMaze datasets. Use the guidance below when making
changes or running tooling.

## Quick Start
- Python version must be 3.13.
- Use `uv` for environment and dependencies: `uv sync`.
- Task runner is `task` (see `Taskfile.yml`).

## Common Tasks
- Run tests: `task test`
- Format: `task ruff-format`
- Lint: `task ruff-check`
- Type checks: `task pyrefly`, `task ty`
- Build UI (Qt Designer): `task build-ui`
- Build resources: `task build-resources`
- Build stylesheets (SCSS -> QSS): `task qss`
- Run app: `uv run tse-analytics`

## Generated Files (Do Not Commit)
- `*_ui.py` files are generated from `.ui` files with `pyside6-uic`.
- `*_rc.py` files are generated from `.qrc` files with `pyside6-rcc`.

## Code Style
- Ruff is the formatter and linter; line length is 120.
- Docstrings follow Google style.
- Use type hints for public APIs (Python 3.13 syntax).
- Use `loguru` (`from loguru import logger`) instead of stdlib logging.

## Project Layout (Top Level)
- `tse_analytics/`: application code (core, modules, toolbox, views, pipeline, styles)
- `tests/`: pytest suite
- `resources/`: app resources (icons, etc.)
- `docs/`: documentation
- `scripts/`, `setup/`: tooling and deployment

## UI/Resource Workflow
- After editing `.ui` files, run the appropriate `task build-ui:*` target or `task build-ui`.
- After editing `resources/`, run `task build-resources`.
- After editing `tse_analytics/styles/scss`, run `task qss`.
