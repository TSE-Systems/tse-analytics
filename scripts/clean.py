#!/usr/bin/env python
"""Clean all build, test, coverage and Python artifacts."""

import shutil
from pathlib import Path

SOURCE_DIR = "tse_analytics"

DIRS_TO_REMOVE = [
    "__pycache__",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    "tse_analytics.egg-info",
]


def remove_dir(path: Path):
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
        print(f"  Removed: {path}")


def main():
    print("Cleaning project artifacts...")

    # Remove top-level directories
    for dir_name in DIRS_TO_REMOVE:
        remove_dir(Path(dir_name))

    # Remove generated *_ui.py and *_rc.py files
    source_path = Path(SOURCE_DIR)
    for pattern in ("**/*_ui.py", "**/*_rc.py"):
        for file in source_path.glob(pattern):
            file.unlink()
            print(f"  Removed: {file}")

    # Remove __pycache__ directories recursively
    for pycache in source_path.rglob("__pycache__"):
        remove_dir(pycache)

    print("\nClean complete.")


if __name__ == "__main__":
    main()
