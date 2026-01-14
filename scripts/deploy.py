#!/usr/bin/env python
"""Deploy the application using PyInstaller."""

import subprocess
import sys


def main():
    # Sync dependencies
    sync_result = subprocess.run(["uv", "sync"])
    if sync_result.returncode != 0:
        sys.exit(sync_result.returncode)

    # Build with PyInstaller
    result = subprocess.run(["pyinstaller", "--clean", "setup/tse-analytics.spec"])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
