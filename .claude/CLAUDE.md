# CLAUDE.md

TSE Analytics — PySide6 desktop app for analyzing TSE PhenoMaster, IntelliCage and IntelliMaze experimental data.

## Quick Start

- Python version must be 3.14.
- Use `uv` for environment and dependencies: `uv sync`.
- Task runner is `task` (see `Taskfile.yml`).
- Data analysis pipeline editor is based on NodeGraphQt library.
- UI is built with PySide6.
- With Pandas always use numpy-nullable data types.

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
