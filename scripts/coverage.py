#!/usr/bin/env python
"""Check code coverage."""

import subprocess
import sys

SOURCE_DIR = "tse_analytics"


def main():
    cmd = ["pytest", f"--cov={SOURCE_DIR}", "tests/"]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
