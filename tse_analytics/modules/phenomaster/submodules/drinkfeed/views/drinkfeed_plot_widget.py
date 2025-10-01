import pandas as pd
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar

from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.submodules.drinkfeed.views.drinkfeed_plot_view import DrinkFeedPlotView
from tse_analytics.views.misc.variable_selector import VariableSelector


class DrinkFeedPlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.variableSelector = VariableSelector(toolbar)
        self.variableSelector.currentTextChanged.connect(self._variable_changed)
        toolbar.addWidget(self.variableSelector)

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self.plotView = DrinkFeedPlotView(self)
        self._layout.addWidget(self.plotView)

    def _variable_changed(self, variable: str):
        self.plotView.set_variable(variable)

    def set_variables(self, variables: dict[str, Variable]):
        self.variableSelector.set_data(variables)

    def set_data(self, df: pd.DataFrame):
        self.plotView.set_data(df)
