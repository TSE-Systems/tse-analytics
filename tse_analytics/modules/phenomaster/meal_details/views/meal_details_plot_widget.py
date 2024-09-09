import pandas as pd
from PySide6.QtWidgets import QWidget

from tse_analytics.core.data.shared import Variable
from tse_analytics.modules.phenomaster.meal_details.views.meal_details_plot_widget_ui import Ui_MealDetailsPlotWidget


class MealDetailsPlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_MealDetailsPlotWidget()
        self.ui.setupUi(self)

        self.ui.variableSelector.currentTextChanged.connect(self._variable_changed)

    def _variable_changed(self, variable: str):
        self.ui.plotView.set_variable(variable)

    def set_variables(self, variables: dict[str, Variable]):
        self.ui.variableSelector.set_data(variables)

    def set_data(self, df: pd.DataFrame):
        self.ui.plotView.set_data(df)
