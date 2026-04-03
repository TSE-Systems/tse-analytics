"""
Workspace service for TSE Analytics.

Manages workspace lifecycle operations: creating, loading, saving,
and accessing the current workspace.
"""

import gc
import pickle

from PySide6.QtCore import QTimer

from tse_analytics.core import messaging
from tse_analytics.core.data.storage import load_workspace as _load_from_duckdb
from tse_analytics.core.data.storage import save_workspace as _save_to_duckdb
from tse_analytics.core.data.workspace import Workspace
from tse_analytics.core.services.selection_service import SelectionService


class WorkspaceService:
    """Manages workspace lifecycle: create, load, save, and access.

    Broadcasts ``WorkspaceChangedMessage`` after workspace modifications
    and delegates selection cleanup to ``SelectionService``.
    """

    def __init__(self, selection: SelectionService):
        self._workspace = Workspace(name="Workspace")
        self._selection = selection

    def get_workspace(self) -> Workspace:
        """Get the current workspace.

        Returns:
            The current workspace object.
        """
        return self._workspace

    def new_workspace(self) -> None:
        """Create a new empty workspace and clear selections."""
        self._workspace = Workspace(name="Workspace")
        self._cleanup_workspace()

    def load_workspace(self, path: str) -> None:
        """Load a workspace from a file and clear selections.

        Supports both DuckDB (``.duckdb``) and legacy pickle (``.workspace``) formats.

        Args:
            path: The path to the workspace file to load.
        """
        if path.endswith(".workspace"):
            with open(path, "rb") as file:
                self._workspace = pickle.load(file)
        else:
            self._workspace = _load_from_duckdb(path)
        self._cleanup_workspace()

    def save_workspace(self, path: str) -> None:
        """Save the current workspace to a file.

        Supports both DuckDB (``.duckdb``) and legacy pickle (``.workspace``) formats.

        Args:
            path: The path where the workspace file will be saved.
        """
        if path.endswith(".workspace"):
            with open(path, "wb") as file:
                pickle.dump(self._workspace, file)
        else:
            _save_to_duckdb(path, self._workspace)

    def _cleanup_workspace(self) -> None:
        """Clean up the workspace by clearing selections and triggering garbage collection.

        Called after operations that significantly change the workspace,
        such as loading a new workspace or removing a dataset.
        """
        self._selection.clear()
        messaging.broadcast(messaging.WorkspaceChangedMessage(self, self._workspace))
        QTimer.singleShot(1000, gc.collect)
