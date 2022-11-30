from typing import Optional

from PySide6.QtWidgets import QWidget

from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import ClearDataMessage, DatasetChangedMessage
from tse_datatools.data.variable import Variable


class AnalysisWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        MessengerListener.__init__(self)
        self.register_to_messenger(Manager.messenger)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self._on_clear_data)

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.update_variables(message.data.variables)

    def _on_clear_data(self, message: ClearDataMessage):
        self.clear()

    def clear(self):
        pass

    def update_variables(self, variables: dict[str, Variable]):
        pass
