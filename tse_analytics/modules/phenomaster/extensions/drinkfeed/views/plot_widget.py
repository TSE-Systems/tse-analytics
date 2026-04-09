import pandas as pd
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QToolBar, QVBoxLayout, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.modules.phenomaster.extensions.drinkfeed.views.plot_view import PlotView
from tse_analytics.views.misc.variable_selector import VariableSelector


class PlotWidget(QWidget):
    def __init__(self, datatable: Datatable, parent: QWidget | None = None):
        super().__init__(parent)

        self.datatable = datatable
        self.filter_mask: pd.Series | None = None

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
        self.variableSelector.set_data(datatable.variables)
        self.variableSelector.currentTextChanged.connect(self._variable_changed)
        toolbar.addWidget(self.variableSelector)

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self.plotView = PlotView(self)
        self.plotView.set_data(self.datatable.df)
        self._layout.addWidget(self.plotView)

        self.plotView.set_variable(next(iter(datatable.variables)))

    def _variable_changed(self, variable: str):
        self.plotView.set_variable(variable)

    def set_filter_mask(self, filter_mask: pd.Series | None) -> None:
        self.filter_mask = filter_mask
        if self.filter_mask is not None:
            df = self.datatable.df[self.filter_mask]
        else:
            df = self.datatable.df
        self.plotView.set_data(df)
