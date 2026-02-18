# Commands

All commands use [Task](https://taskfile.dev/) runner (see `Taskfile.yml`):

```
task test              # run pytest
task ruff-format       # format code
task ruff-check        # lint
task ruff-fix          # auto-fix lint issues
task pyrefly           # type check (pyrefly)
task ty                # type check (ty)
task build-ui          # compile all .ui → *_ui.py
task build-resources   # compile .qrc → *_rc.py
task qss               # compile SCSS → QSS stylesheets
task deploy            # PyInstaller build
uv run tse-analytics   # run the app
```

Package manager is **uv**. Use `uv sync` to install dependencies.
