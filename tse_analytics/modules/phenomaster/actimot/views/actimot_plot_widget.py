import pandas as pd
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.actimot.views.actimot_plot_widget_ui import Ui_ActimotPlotWidget


class ActimotPlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ActimotPlotWidget()
        self.ui.setupUi(self)

        self.ui.variableSelector.currentTextChanged.connect(self.__variable_changed)

    def __variable_changed(self, variable: str):
        self.ui.plotView.set_variable(variable)

    def set_variables(self, variables: dict[str, Variable]):
        self.ui.variableSelector.set_data(variables)

    def set_data(self, df: pd.DataFrame):
        self.ui.plotView.set_data(df)
