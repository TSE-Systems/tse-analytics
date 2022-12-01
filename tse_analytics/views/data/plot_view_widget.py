from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLabel, QComboBox

from tse_analytics.core.manager import Manager
from tse_analytics.views.data.data_widget import DataWidget
from tse_analytics.views.data.plot_view import PlotView
from tse_datatools.data.variable import Variable


class PlotViewWidget(DataWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.plot_view = PlotView(self)
        self.variable_combo_box = QComboBox(self)
        self.variables = []

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.plot_view)

    def clear(self):
        self.plot_view.clear_plot()
        self.variables.clear()
        self.variable_combo_box.clear()

    def assign_data(self):
        df = Manager.data.get_current_df()
        self.plot_view.set_data(df)

    def set_variables(self, variables: dict[str, Variable]):
        self.variables.clear()
        for var in variables:
            self.variables.append(var)
        self.variable_combo_box.clear()
        self.variable_combo_box.addItems(self.variables)
        self.variable_combo_box.setCurrentText('')

    def clear_selection(self):
        # self.plot_view.clear()
        self.plot_view.set_data(Manager.data.selected_dataset.original_df)

    def _variable_current_text_changed(self, variable: str):
        Manager.data.selected_variable = variable
        self.plot_view.set_variable(variable)

    def _display_errors(self, state: bool):
        self.plot_view.set_display_errors(state)

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

        display_errors_action = QAction(QIcon(":/icons/icons8-sorting-16.png"), "Display Errors", self)
        display_errors_action.triggered.connect(self._display_errors)
        display_errors_action.setCheckable(True)
        toolbar.addAction(display_errors_action)

        return toolbar
