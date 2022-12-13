from typing import Optional

from PySide6.QtWidgets import QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import (
    BinningAppliedMessage,
    ClearDataMessage,
    DataChangedMessage,
    DatasetChangedMessage,
    GroupingModeChangedMessage,
    RevertBinningMessage,
)
from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_datatools.data.variable import Variable


class DataWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        MessengerListener.__init__(self)
        self.register_to_messenger(Manager.messenger)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self._on_clear_data)
        messenger.subscribe(self, BinningAppliedMessage, self._on_binning_applied)
        messenger.subscribe(self, RevertBinningMessage, self._on_revert_binning)
        messenger.subscribe(self, DataChangedMessage, self._on_data_changed)
        messenger.subscribe(self, GroupingModeChangedMessage, self._on_grouping_mode_changed)

    def clear(self):
        pass

    def clear_selection(self):
        pass

    def set_variables(self, variables: dict[str, Variable]):
        pass

    def assign_data(self):
        pass

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.set_variables(message.data.variables)
        self.assign_data()

    def _on_binning_applied(self, message: BinningAppliedMessage):
        self.assign_data()

    def _on_data_changed(self, message: DataChangedMessage):
        self.assign_data()

    def _on_clear_data(self, message: ClearDataMessage):
        self.clear()

    def _on_grouping_mode_changed(self, message: GroupingModeChangedMessage):
        self.assign_data()

    def _on_revert_binning(self, message: RevertBinningMessage):
        self.clear_selection()
