from typing import Optional

import pandas as pd
from PySide6.QtWidgets import QWidget

from tse_analytics.views.calo_details.calo_details_plot_widget_ui import Ui_CaloDetailsPlotWidget
from tse_datatools.data.variable import Variable


class CaloDetailsPlotWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.ui = Ui_CaloDetailsPlotWidget()
        self.ui.setupUi(self)

        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)
        self.ui.toolButtonDisplayErrors.toggled.connect(self.__display_errors)

    def __variable_changed(self, variable: str):
        self.ui.plotView.set_variable(variable)

    def __display_errors(self, state: bool):
        self.ui.plotView.set_display_errors(state)

    def set_variables(self, variables: dict[str, Variable]):
        self.ui.variableSelector.set_data(variables)

    def set_data(self, df: pd.DataFrame):
        self.ui.plotView.set_data(df)
