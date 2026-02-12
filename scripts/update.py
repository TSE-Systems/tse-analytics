#!/usr/bin/env python
"""Update uv and project dependencies."""

import subprocess
import sys


def main():
    commands = [
        ["uv", "self", "update"],
        ["uv", "lock", "--upgrade"],
        ["uv", "sync"],
    ]

    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            sys.exit(result.returncode)

    print("\nUpdate complete.")


if __name__ == "__main__":
    main()
