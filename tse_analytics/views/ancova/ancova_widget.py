from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QComboBox, QTabWidget, QPushButton

from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetRemovedMessage, DatasetUnloadedMessage, \
    DatasetComponentChangedMessage
from tse_analytics.views.ancova.pairwise_comparison_widget import PairwiseComparisonWidget


class AncovaWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        self.register_to_messenger(Manager.messenger)

        self.tabWidget = QTabWidget(self)

        self.variables = list()

        self.covariate_combo_box = QComboBox(self)
        self.covariate = ""

        self.response_combo_box = QComboBox(self)
        self.response = ""

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.tabWidget)

        self.pairwise_comparison_widget = PairwiseComparisonWidget()
        self.tabWidget.addTab(self.pairwise_comparison_widget, QIcon(":/icons/icons8-scales-16.png"), "One-way ANCOVA")

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetComponentChangedMessage, self._on_dataset_component_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_dataset_removed)
        messenger.subscribe(self, DatasetUnloadedMessage, self._on_dataset_unloaded)

    def clear(self):
        self.variables.clear()
        self.covariate_combo_box.clear()
        self.response_combo_box.clear()
        self.pairwise_comparison_widget.clear()

    def _on_dataset_component_changed(self, message: DatasetComponentChangedMessage):
        self.variables.clear()
        self.covariate = ""
        self.response = ""
        for param in message.data.meta.get("Parameters"):
            self.variables.append(param.get("Name"))

        self.covariate_combo_box.clear()
        self.covariate_combo_box.addItems(self.variables)
        self.covariate_combo_box.setCurrentText("")

        self.response_combo_box.clear()
        self.response_combo_box.addItems(self.variables)
        self.response_combo_box.setCurrentText("")

    def _on_dataset_removed(self, message: DatasetRemovedMessage):
        self.clear()

    def _on_dataset_unloaded(self, message: DatasetUnloadedMessage):
        self.clear()

    def _covariate_current_text_changed(self, covariate: str):
        self.covariate = covariate

    def _response_current_text_changed(self, response: str):
        self.response = response

    def _analyze(self):
        if Manager.data.selected_dataset_component is None:
            return

        df = Manager.data.selected_dataset_component.filter_by_groups(Manager.data.selected_groups)

        self.pairwise_comparison_widget.analyze(df, self.covariate, self.response)

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        toolbar.addWidget(QLabel("Covariate: "))

        self.covariate_combo_box.addItems(self.variables)
        self.covariate_combo_box.setCurrentText("")
        self.covariate_combo_box.currentTextChanged.connect(self._covariate_current_text_changed)
        toolbar.addWidget(self.covariate_combo_box)

        toolbar.addWidget(QLabel("Response: "))

        self.response_combo_box.addItems(self.variables)
        self.response_combo_box.setCurrentText("")
        self.response_combo_box.currentTextChanged.connect(self._response_current_text_changed)
        toolbar.addWidget(self.response_combo_box)

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self._analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
