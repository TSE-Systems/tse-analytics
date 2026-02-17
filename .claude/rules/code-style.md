# Code Style

- **Formatter/Linter**: Ruff — line length 120, target Python 3.14
- **Docstrings**: Google convention
- **Type hints**: modern syntax (`list[str]`, `dict[str, int]`, `X | None`)
- **Logging**: `from loguru import logger` (not stdlib `logging`)
- **Naming**: `PascalCase` classes, `snake_case` functions, `UPPER_SNAKE_CASE` constants, `_prefix` for private
- **Imports**: stdlib → third-party → local (`tse_analytics.*`); sorted by `isort` (via ruff)
