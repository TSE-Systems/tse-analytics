"""
Entry point module for running the TSE Analytics package as a script.

This module provides the entry point for running the package using 'python -m tse_analytics'.
It initializes multiprocessing support and calls the main function from the app module.
"""

from multiprocessing import freeze_support

from tse_analytics.app import main

if __name__ == "__main__":
    # See https://docs.python.org/3/library/multiprocessing.html#multiprocessing.freeze_support
    freeze_support()
    main()
