#!/usr/bin/env python
"""Run tests."""

import subprocess
import sys


def main():
    result = subprocess.run(["pytest"])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
