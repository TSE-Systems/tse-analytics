"""
Module containing the Workspace class for managing multiple datasets.

This module provides functionality for organizing and managing multiple datasets
within a workspace.
"""

from dataclasses import dataclass, field
from uuid import UUID

from tse_analytics.core.data.dataset import Dataset


@dataclass
class Workspace:
    """
    A class representing a workspace containing multiple datasets.

    The Workspace class provides a container for organizing and managing
    multiple datasets.

    Attributes
    ----------
    name : str
        The name of the workspace.
    datasets : dict[UUID, Dataset]
        Dictionary mapping dataset UUIDs to Dataset instances.
    """

    name: str
    datasets: dict[UUID, Dataset] = field(default_factory=dict)
