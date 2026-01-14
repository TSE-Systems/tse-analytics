#!/usr/bin/env python
"""Run linting tools (mypy, ty, pylint, ruff)."""

import argparse
import subprocess
import sys

SOURCE_DIR = "tse_analytics"


def run_mypy():
    print("Running mypy...")
    return subprocess.run(["mypy", SOURCE_DIR]).returncode


def run_ty():
    print("Running ty...")
    subprocess.run(["ty", "check"])  # ignore errors as in original
    return 0


def run_pylint():
    print("Running pylint...")
    subprocess.run(["pylint", "-j", "8", SOURCE_DIR])  # ignore errors as in original
    return 0


def run_ruff_check():
    print("Running ruff check...")
    subprocess.run(["ruff", "check", "."])  # ignore errors as in original
    return 0


def run_ruff_fix():
    print("Running ruff check --fix...")
    subprocess.run(["ruff", "check", ".", "--fix"])  # ignore errors as in original
    return 0


def run_ruff_format():
    print("Running ruff format...")
    subprocess.run(["ruff", "format", "."])  # ignore errors as in original
    return 0


def main():
    parser = argparse.ArgumentParser(description="Run linting tools")
    parser.add_argument(
        "tool",
        choices=["mypy", "ty", "pylint", "ruff-check", "ruff-fix", "ruff-format", "all"],
        help="Linting tool to run",
    )
    args = parser.parse_args()

    if args.tool == "mypy":
        sys.exit(run_mypy())
    elif args.tool == "ty":
        sys.exit(run_ty())
    elif args.tool == "pylint":
        sys.exit(run_pylint())
    elif args.tool == "ruff-check":
        sys.exit(run_ruff_check())
    elif args.tool == "ruff-fix":
        sys.exit(run_ruff_fix())
    elif args.tool == "ruff-format":
        sys.exit(run_ruff_format())
    elif args.tool == "all":
        run_mypy()
        run_ty()
        run_pylint()
        run_ruff_check()


if __name__ == "__main__":
    main()
