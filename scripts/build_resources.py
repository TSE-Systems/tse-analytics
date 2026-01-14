#!/usr/bin/env python
"""Build Qt resources file."""

import subprocess
import sys


def main():
    cmd = ["pyside6-rcc", "resources/resources.qrc", "-o", "tse_analytics/resources_rc.py"]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
