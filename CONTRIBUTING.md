# Contributing to TSE Analytics

Thank you for your interest in contributing to TSE Analytics! This document provides guidelines and instructions for developers working on this project.

## Development Setup

### Prerequisites

- **Python 3.13.11** (exact version required)
- **uv** package manager ([installation guide](https://github.com/astral-sh/uv))
- **Task** task runner ([installation guide](https://taskfile.dev/installation/))
- Git for version control

### Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/TSE-Systems/tse-analytics.git
   cd tse-analytics
   ```

2. Create and activate virtual environment with uv:
   ```bash
   uv sync
   ```

3. Verify installation:
   ```bash
   task test
   ```

## Code Style and Quality

### Code Formatting

This project uses **Ruff** for both linting and formatting:

- **Line length**: 120 characters
- **Target version**: Python 3.13
- **Docstring convention**: Google style
- **Indentation**: 4 spaces (configured in `.editorconfig`)
- **Line endings**: LF (Unix-style)
- **Character encoding**: UTF-8

### Linting and Type Checking

The project uses multiple tools for code quality:

- **Ruff**: Primary linter and formatter
- **ty**: Type analysis
- **pyrefly**: Project-specific type checking

### Running Quality Checks

```bash
# Format code
task ruff-format

# Check for issues
task ruff-check

# Auto-fix issues
task ruff-fix

# Run type checking
task pyrefly
task ty

# Run all tests
task test
```

## Project Structure

```
tse-analytics/
├── tse_analytics/          # Main source code
│   ├── core/              # Core functionality
│   ├── modules/           # Feature modules (phenomaster, intellicage, intellimaze)
│   ├── toolbox/           # Analysis tools (ANOVA, PCA, etc.)
│   ├── views/             # UI components
│   ├── pipeline/          # Data processing pipeline
│   └── styles/            # UI styles (SCSS/QSS)
├── tests/                 # Test suite
├── docs/                  # Documentation
├── resources/             # Application resources
├── scripts/               # Utility scripts
├── setup/                 # Deployment configuration
├── pyproject.toml         # Project configuration
├── Taskfile.yml           # Task definitions
└── .editorconfig          # Editor configuration
```

### Important Notes

- **Do NOT commit auto-generated files**: Files ending with `*_ui.py` and `*_rc.py` are generated from Qt Designer `.ui` files and resource files. They are excluded from version control.
- **Module organization**: Each module (phenomaster, intellicage, intellimaze) is self-contained with its own data, views, and models.

## Development Workflow

### Working with PySide6 UI Files

UI files are created in Qt Designer and must be compiled to Python:

```bash
# Build all UI files
task build-ui

# Build specific module UI files
task build-ui:views
task build-ui:toolbox
task build-ui:phenomaster
task build-ui:intellicage
task build-ui:intellimaze
```

### Building Resources

After modifying resources (icons, images, etc.):

```bash
task build-resources
```

### Building Stylesheets

After modifying SCSS files:

```bash
task qss
```

### Running the Application

```bash
# Using uv
uv run tse-analytics

# Or using the installed script
tse-analytics
```

## Testing

### Running Tests

```bash
# Run all tests
task test

# Run tests with coverage
task coverage

# Run specific test file
pytest tests/test_specific.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Follow pytest conventions
- Aim for meaningful test coverage
- Mock external dependencies when appropriate

## Code Guidelines

### Python Code Style

1. **Imports**:
   - Standard library imports first
   - Third-party imports second
   - Local imports last
   - Use absolute imports from `tse_analytics`

2. **Naming Conventions**:
   - Classes: `PascalCase`
   - Functions/methods: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
   - Private members: prefix with `_`

3. **Docstrings**:
   - Use Google-style docstrings
   - Document all public classes, methods, and functions
   - Include Args, Returns, and Raises sections where applicable

4. **Type Hints**:
   - Use type hints for function parameters and return values
   - Use modern Python 3.13 type syntax (e.g., `list[str]` instead of `List[str]`)

5. **Logging**:
   - Use `loguru` for logging (not standard `logging`)
   - Import: `from loguru import logger`
   - Use appropriate log levels: `debug`, `info`, `warning`, `error`, `critical`

### Example Code

```python
from pathlib import Path

from loguru import logger
from PySide6.QtWidgets import QWidget


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

    def process_dataset(self, dataset_id: str) -> dict[str, any]:
        """Process a single dataset.

        Args:
            dataset_id: Unique identifier for the dataset.

        Returns:
            Dictionary containing processed data and metadata.

        Raises:
            ValueError: If dataset_id is invalid.
            FileNotFoundError: If dataset files are missing.
        """
        if not dataset_id:
            raise ValueError("Dataset ID cannot be empty")

        logger.info(f"Processing dataset: {dataset_id}")
        # Implementation here
        return {}
```

## Git Workflow

### Branching Strategy

- `main`: Stable production code
- Feature branches: `feature/description`
- Bug fixes: `bugfix/description`
- Releases: `release/version`

### Commit Messages

Write clear, descriptive commit messages:

```
Short summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain what changed and why, not how.

- Bullet points are acceptable
- Use present tense ("Add feature" not "Added feature")
- Reference issues/PRs if applicable
```

### Before Committing

1. Run code formatting:
   ```bash
   task ruff-format
   ```

2. Check for issues:
   ```bash
   task ruff-check
   task mypy
   ```

3. Run tests:
   ```bash
   task test
   ```

4. Build UI files if modified:
   ```bash
   task build-ui
   ```

### Pull Request Guidelines

1. **Title**: Clear and descriptive
2. **Description**: Explain what changed and why
3. **Testing**: Describe how you tested the changes
4. **Screenshots**: Include for UI changes
5. **Checklist**:
   - [ ] Code follows style guidelines
   - [ ] Tests added/updated
   - [ ] Documentation updated if needed
   - [ ] All tests pass
   - [ ] No linting errors

## Dependency Management

### Adding Dependencies

1. Add to `pyproject.toml` under `dependencies` or `dependency-groups.dev`
2. Run `uv sync` to install
3. Commit both `pyproject.toml` and `uv.lock`

### Updating Dependencies

```bash
# Update all dependencies
task update

# Update specific package
uv add package@latest
```

## Building and Deployment

### Creating a Distribution

```bash
# Using PyInstaller
task deploy

# Using PySide6 deployment
task deploy-pyside
```

### Cleaning Build Artifacts

```bash
task clean
```

## Getting Help

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/TSE-Systems/tse-analytics/issues)
- **Documentation**: See the `docs/` directory
- **Code Questions**: Review existing code and tests for examples

## License

By contributing to TSE Analytics, you agree that your contributions will be licensed under the GPL-3.0-or-later license.
