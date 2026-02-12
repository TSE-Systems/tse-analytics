"""
Selection service for TSE Analytics.

Manages the currently selected dataset and datatable state, broadcasting
change messages when selections are updated.
"""

from tse_analytics.core import messaging
from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.datatable import Datatable


class SelectionService:
    """Manages the selected dataset and datatable state.

    Broadcasts ``DatasetChangedMessage`` and ``DatatableChangedMessage``
    whenever the selection changes.
    """

    def __init__(self):
        self._selected_dataset: Dataset | None = None
        self._selected_datatable: Datatable | None = None

    def get_selected_dataset(self) -> Dataset | None:
        """Get the currently selected dataset.

        Returns:
            The currently selected dataset, or None if no dataset is selected.
        """
        return self._selected_dataset

    def set_selected_dataset(self, dataset: Dataset | None) -> None:
        """Set the currently selected dataset and broadcast a change message.

        Args:
            dataset: The dataset to select, or None to clear the selection.
        """
        self._selected_dataset = dataset
        messaging.broadcast(messaging.DatasetChangedMessage(self, dataset))

    def get_selected_datatable(self) -> Datatable | None:
        """Get the currently selected datatable.

        Returns:
            The currently selected datatable, or None if no datatable is selected.
        """
        return self._selected_datatable

    def set_selected_datatable(self, datatable: Datatable | None) -> None:
        """Set the currently selected datatable and broadcast a change message.

        Args:
            datatable: The datatable to select, or None to clear the selection.
        """
        self._selected_datatable = datatable
        messaging.broadcast(messaging.DatatableChangedMessage(self, datatable))

    def clear(self) -> None:
        """Clear both dataset and datatable selections."""
        self.set_selected_datatable(None)
        self.set_selected_dataset(None)
