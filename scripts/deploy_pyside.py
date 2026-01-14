#!/usr/bin/env python
"""Deploy the application using PySide6-deploy."""

import subprocess
import sys


def main():
    # Sync dependencies
    sync_result = subprocess.run(["uv", "sync"])
    if sync_result.returncode != 0:
        sys.exit(sync_result.returncode)

    # Build with pyside6-deploy
    result = subprocess.run(["pyside6-deploy", "-c", "pysidedeploy.spec"])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
