# CLAUDE.md

TSE Analytics — PySide6 desktop app for analyzing TSE PhenoMaster, IntelliCage, and IntelliMaze experimental data.

## Quick Start

- Python version must be 3.14.
- Use `uv` for environment and dependencies: `uv sync`.
- Task runner is `task` (see `Taskfile.yml`).
- Data analysis pipeline editor is based on NodeGraphQt library.
- UI is built with PySide6.

## Generated Files — Do Not Edit or Commit

- `*_ui.py` — generated from `.ui` files via `pyside6-uic`
- `*_rc.py` — generated from `.qrc` files via `pyside6-rcc`

After editing `.ui` files run `task build-ui`. After editing resources run `task build-resources`. After editing SCSS run `task qss`.

## Dependencies

- Add deps in `pyproject.toml` under `dependencies` or `dependency-groups.dev`
- Run `uv sync` to install; commit both `pyproject.toml` and `uv.lock`
- Update all: `task update`
