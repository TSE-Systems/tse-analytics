from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QComboBox

from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetRemovedMessage, AnimalDataChangedMessage, \
    DatasetChangedMessage
from tse_analytics.views.charts.chart_view import ChartView


class ChartViewWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        self.register_to_messenger(Manager.messenger)

        self.chart_view = ChartView(self)
        self.variable_combo_box = QComboBox(self)

        self.variables = []

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.chart_view)

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, AnimalDataChangedMessage, self._on_animal_data_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_dataset_removed)

    def clear(self):
        self.chart_view.clear()
        self.variables.clear()
        self.variable_combo_box.clear()

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.variables.clear()
        for var in message.data.variables:
            self.variables.append(var)
        self.variable_combo_box.clear()
        self.variable_combo_box.addItems(self.variables)
        self.variable_combo_box.setCurrentText('')
        self.chart_view.set_data(message.data)

    def _on_animal_data_changed(self, message: AnimalDataChangedMessage):
        self.chart_view.set_animal_data(message.animals)

    def _on_dataset_removed(self, message: DatasetRemovedMessage):
        self.clear()

    def _variable_current_text_changed(self, variable: str):
        self.chart_view.set_variable(variable)

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar(self)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        label = QLabel("Variable: ")
        toolbar.addWidget(label)

        self.variable_combo_box.addItems(self.variables)
        self.variable_combo_box.setCurrentText('')
        self.variable_combo_box.currentTextChanged.connect(self._variable_current_text_changed)
        toolbar.addWidget(self.variable_combo_box)

        return toolbar
