from typing import Optional

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from tse_analytics.messaging.messenger import Messenger
from tse_analytics.messaging.messenger_listener import MessengerListener
from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import ClearDataMessage, DatasetChangedMessage
from tse_analytics.views.analysis.ancova_widget import AncovaWidget
from tse_analytics.views.analysis.anova_widget import AnovaWidget
from tse_analytics.views.analysis.correlation_widget import CorrelationWidget
from tse_analytics.views.analysis.distribution_widget import DistributionWidget
from tse_analytics.views.analysis.glm_widget import GlmWidget
from tse_analytics.views.analysis.normality_widget import NormalityWidget


class AnalysisWidget(QWidget, MessengerListener):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        MessengerListener.__init__(self)
        self.register_to_messenger(Manager.messenger)

        self.tabWidget = QTabWidget(self)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.tabWidget)

        self.distribution_widget = DistributionWidget()
        self.tabWidget.addTab(self.distribution_widget, QIcon(":/icons/icons8-bar-chart-16.png"), "Distribution")

        self.normality_widget = NormalityWidget()
        self.tabWidget.addTab(self.normality_widget, QIcon(":/icons/icons8-approval-16.png"), "Normality Check")

        self.correlation_widget = CorrelationWidget()
        self.tabWidget.addTab(self.correlation_widget, QIcon(":/icons/icons8-scales-16.png"), "Correlation")

        self.anova_widget = AnovaWidget()
        self.tabWidget.addTab(self.anova_widget, QIcon(":/icons/icons8-scales-16.png"), "ANOVA")

        self.ancova_widget = AncovaWidget()
        self.tabWidget.addTab(self.ancova_widget, QIcon(":/icons/icons8-scales-16.png"), "ANCOVA")

        self.glm_widget = GlmWidget()
        self.tabWidget.addTab(self.glm_widget, QIcon(":/icons/icons8-scales-16.png"), "GLM")

    def register_to_messenger(self, messenger: Messenger):
        messenger.subscribe(self, DatasetChangedMessage, self._on_dataset_changed)
        messenger.subscribe(self, ClearDataMessage, self._on_clear_data)

    def _clear(self):
        self.distribution_widget.clear()
        self.normality_widget.clear()
        self.correlation_widget.clear()
        self.anova_widget.clear()
        self.ancova_widget.clear()
        self.glm_widget.clear()

    def _on_dataset_changed(self, message: DatasetChangedMessage):
        self.distribution_widget.update_variables(message.data.variables)
        self.normality_widget.update_variables(message.data.variables)
        self.anova_widget.update_variables(message.data.variables)
        self.correlation_widget.update_variables(message.data.variables)
        self.ancova_widget.update_variables(message.data.variables)
        self.glm_widget.update_variables(message.data.variables)

    def _on_clear_data(self, message: ClearDataMessage):
        self._clear()
