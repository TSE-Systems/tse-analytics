from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QLabel, QToolBar, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.views.data.data_widget import DataWidget
from tse_analytics.views.data.plot_view import PlotView
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_datatools.data.variable import Variable


class PlotViewWidget(DataWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.variable_selector = VariableSelector()
        self.variable_selector.currentTextChanged.connect(self.__variable_changed)

        self.plot_view = PlotView(self)

        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.plot_view)

    def clear(self):
        self.variable_selector.clear()
        self.plot_view.clear_plot()

    def assign_data(self):
        df = Manager.data.get_current_df()
        self.plot_view.set_data(df)

    def set_variables(self, variables: dict[str, Variable]):
        self.variable_selector.set_data(variables)

    def clear_selection(self):
        # self.plot_view.clear()
        self.plot_view.set_data(Manager.data.selected_dataset.original_df)

    def __variable_changed(self, variable: str):
        Manager.data.selected_variable = variable
        self.plot_view.set_variable(variable)

    def _display_errors(self, state: bool):
        self.plot_view.set_display_errors(state)

    @property
    def toolbar(self) -> QToolBar:
        toolbar = QToolBar(self)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        toolbar.addWidget(QLabel("Variable: "))
        toolbar.addWidget(self.variable_selector)

        display_errors_action = QAction(QIcon(":/icons/icons8-sorting-16.png"), "Display Errors", self)
        display_errors_action.triggered.connect(self._display_errors)
        display_errors_action.setCheckable(True)
        toolbar.addAction(display_errors_action)

        return toolbar
