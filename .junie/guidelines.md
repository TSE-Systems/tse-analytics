# TSE Analytics Developer Guidelines

## Project Overview
TSE Analytics is a data analysis application for working with TSE PhenoMaster data. It provides functionality for dataset management, data processing, visualization, and statistical analysis.

## Project Structure
- **tse_analytics/**: Main package
  - **core/**: Core functionality and business logic
  - **modules/**: Domain-specific modules (phenomaster, intellicage, intellimaze)
  - **views/**: UI components and views
  - **styles/**: UI styling (SCSS/QSS)
- **docs/**: User documentation
- **resources/**: Application resources
- **setup/**: Installation and packaging

## Tech Stack
- **Python 3.13.5**: Required specific version
- **UI Framework**: PySide6 (Qt for Python)
- **Data Analysis**: pandas, scikit-learn, matplotlib, seaborn
- **Scientific Computing**: astropy, lmfit
- **Visualization**: pyqtgraph
- **Dependency Management**: uv

## Development Setup
1. Create a virtual environment: `python -m venv .venv`
2. Activate the environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
3. Install dependencies: `uv sync`

## Running the Application
- Run directly: `python -m tse_analytics`
- Use the CLI entry point: `tse-analytics`

## Running Tests
- Run all tests: `task test`
- Run with coverage: `task coverage`

## Code Quality Tools
- Type checking: `task mypy`
- Linting: `task pylint` or `task ruff-check`
- Auto-formatting: `task ruff-format`
- Fix linting issues: `task ruff-fix`

## Building UI Components
- Compile UI files: `task build-ui`
- Compile resources: `task build-resources`
- Compile stylesheets: `task qss`

## Creating Executables
- Build executable: `task create-setup`

## Best Practices
1. **Code Style**: Follow PEP 8 guidelines and use ruff for formatting
2. **Type Hints**: Use type hints for all function parameters and return values
3. **Documentation**: Document classes and functions using Google docstring format
4. **UI Development**:
   - Design UI in Qt Designer (.ui files)
   - Compile UI files with `task build-ui`
   - Don't modify generated *_ui.py files directly
5. **Testing**: Write tests for new functionality
6. **Dependencies**: Use `uv lock --upgrade` and `uv sync` to manage dependencies
7. **Git Workflow**:
   - Create feature branches for new features
   - Write descriptive commit messages
   - Run tests before submitting pull requests
