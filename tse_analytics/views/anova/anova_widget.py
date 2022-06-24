from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QComboBox, QTabWidget, QPushButton

from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import DatasetRemovedMessage, DatasetUnloadedMessage, \
    DatasetComponentChangedMessage
from tse_analytics.views.anova.distribution_widget import DistributionWidget
from tse_analytics.views.anova.normality_widget import NormalityWidget
from tse_analytics.views.anova.pairwise_comparison_widget import PairwiseComparisonWidget


class AnovaWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        MessengerListener.__init__(self)

        self.register_to_messenger(Manager.messenger)

        self.tabWidget = QTabWidget(self)
        self.variable_combo_box = QComboBox(self)
        self.variables = list()
        self.variable = ""

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.tabWidget)

        self.distribution_widget = DistributionWidget()
        self.tabWidget.addTab(self.distribution_widget, QIcon(":/icons/icons8-bar-chart-16.png"), "Distribution")

        self.normality_widget = NormalityWidget()
        self.tabWidget.addTab(self.normality_widget, QIcon(":/icons/icons8-approval-16.png"), "Normality Check")

        self.pairwise_comparison_widget = PairwiseComparisonWidget()
        self.tabWidget.addTab(self.pairwise_comparison_widget, QIcon(":/icons/icons8-scales-16.png"), "Pairwise Comparison")

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetComponentChangedMessage, self._on_dataset_component_changed)
        messenger.subscribe(self, DatasetRemovedMessage, self._on_dataset_removed)
        messenger.subscribe(self, DatasetUnloadedMessage, self._on_dataset_unloaded)

    def clear(self):
        self.variables.clear()
        self.variable_combo_box.clear()
        self.distribution_widget.clear()
        self.normality_widget.clear()
        self.pairwise_comparison_widget.clear()

    def _on_dataset_component_changed(self, message: DatasetComponentChangedMessage):
        self.variables.clear()
        self.variable = ""
        for param in message.data.meta.get("Parameters"):
            self.variables.append(param.get("Name"))
        self.variable_combo_box.clear()
        self.variable_combo_box.addItems(self.variables)
        self.variable_combo_box.setCurrentText("")

    def _on_dataset_removed(self, message: DatasetRemovedMessage):
        self.clear()

    def _on_dataset_unloaded(self, message: DatasetUnloadedMessage):
        self.clear()

    def _variable_current_text_changed(self, variable: str):
        self.variable = variable

    def _analyze(self):
        if Manager.data.selected_dataset_component is None:
            return

        df = Manager.data.selected_dataset_component.filter_by_groups(Manager.data.selected_groups)

        self.distribution_widget.analyze(df, self.variable)
        self.normality_widget.analyze(df, self.variable)
        self.pairwise_comparison_widget.analyze(df, self.variable)

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        label = QLabel("Variable: ")
        toolbar.addWidget(label)

        self.variable_combo_box.addItems(self.variables)
        self.variable_combo_box.setCurrentText("")
        self.variable_combo_box.currentTextChanged.connect(self._variable_current_text_changed)
        toolbar.addWidget(self.variable_combo_box)

        pushButtonAnalyze = QPushButton("Analyze")
        pushButtonAnalyze.clicked.connect(self._analyze)
        toolbar.addWidget(pushButtonAnalyze)

        return toolbar
