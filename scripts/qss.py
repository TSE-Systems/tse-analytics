#!/usr/bin/env python
"""Compile SCSS to QSS stylesheets."""

import subprocess
import sys


def main():
    cmd = ["qtsass", "./tse_analytics/styles/scss", "-o", "./tse_analytics/styles/qss"]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
