"""
Module containing the Workspace class for managing multiple datasets.

This module provides functionality for organizing and managing multiple datasets
within a workspace.
"""

from uuid import UUID

from tse_analytics.core.data.dataset import Dataset


class Workspace:
    """
    A class representing a workspace containing multiple datasets.

    The Workspace class provides a container for organizing and managing
    multiple datasets.
    """

    def __init__(self, name: str):
        """
        Initialize a Workspace instance.

        Parameters
        ----------
        name : str
            The name of the workspace.
        """
        self.name = name
        self.datasets: dict[UUID, Dataset] = {}
