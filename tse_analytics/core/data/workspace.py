"""
Module containing the Workspace class for managing multiple datasets.

This module provides functionality for organizing and managing multiple datasets
within a workspace.
"""

from typing import Any
from uuid import UUID, uuid7

from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from tse_analytics.core.data.dataset import Dataset


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Workspace:
    """
    A class representing a workspace containing multiple datasets.

    The Workspace class provides a container for organizing and managing
    multiple datasets.

    Attributes
    ----------
    id : UUID
        Unique ID of the workspace.
    name : str
        The name of the workspace.
    description : str
        Description of the workspace.
    metadata : dict
        Metadata associated with the workspace.
    datasets : dict[UUID, Dataset]
        Dictionary mapping dataset UUIDs to Dataset instances.
    """

    id: UUID = uuid7()
    name: str = "Untitled Workspace"
    description: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    datasets: dict[UUID, Dataset] = Field(default_factory=dict)
