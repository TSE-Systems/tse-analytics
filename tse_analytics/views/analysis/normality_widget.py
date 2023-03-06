from typing import Optional

import pingouin as pg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtWidgets import QLabel, QWidget

from tse_analytics.core.manager import Manager
from tse_analytics.views.analysis.analysis_widget import AnalysisWidget
from tse_analytics.views.misc.variable_selector import VariableSelector
from tse_datatools.analysis.grouping_mode import GroupingMode
from tse_datatools.data.variable import Variable


class NormalityWidget(AnalysisWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.help_path = "docs/normality.md"

        self.variable = ""
        self.variable_selector = VariableSelector()
        self.variable_selector.currentTextChanged.connect(self.__variable_changed)
        self.toolbar.addWidget(QLabel("Variable: "))
        self.toolbar.addWidget(self.variable_selector)

        figure = Figure(figsize=(5.0, 4.0), dpi=100)
        self.canvas = FigureCanvasQTAgg(figure)

        self.layout().addWidget(NavigationToolbar2QT(self.canvas, self))
        self.layout().addWidget(self.canvas)

    def clear(self):
        self.canvas.figure.clear()

    def update_variables(self, variables: dict[str, Variable]):
        self.variable_selector.set_data(variables)

    def __variable_changed(self, variable: str):
        self.variable = variable

    def _analyze(self):
        if Manager.data.selected_dataset is None or (
            Manager.data.grouping_mode == GroupingMode.FACTORS and Manager.data.selected_factor is None):
            return

        df = Manager.data.selected_dataset.active_df

        self.clear()

        if Manager.data.grouping_mode == GroupingMode.FACTORS:
            if len(Manager.data.selected_factor.groups) == 0:
                self.canvas.figure.suptitle("Please assign animals to groups first")
                self.canvas.draw()
                return

            factor_name = Manager.data.selected_factor.name
            groups = df[factor_name].unique()
            nrows, ncols = self.__get_cells(len(groups))
            for index, group in enumerate(groups):
                ax = self.canvas.figure.add_subplot(nrows, ncols, index + 1)
                # stats.probplot(df[df[factor_name] == group][variable], dist="norm", plot=ax)
                pg.qqplot(df[df[factor_name] == group][self.variable], dist="norm", ax=ax)
                ax.set_title(group)

            self.canvas.figure.tight_layout()
            self.canvas.draw()
        else:
            animals = Manager.data.selected_animals
            nrows, ncols = self.__get_cells(len(animals))
            for index, animal in enumerate(animals):
                ax = self.canvas.figure.add_subplot(nrows, ncols, index + 1)
                # stats.probplot(df[df["Animal"] == group][variable], dist="norm", plot=ax)
                pg.qqplot(df[df["Animal"] == animal.id][self.variable], dist="norm", ax=ax)
                ax.set_title(animal.id)

            self.canvas.figure.tight_layout()
            self.canvas.draw()

    def __get_cells(self, count: int):
        if count == 1:
            return 1, 1
        elif count == 2:
            return 1, 2
        elif count <= 4:
            return 2, 2
        else:
            nrows = count // 2 + (count % 2 > 0)
            ncols = 2
            return nrows, ncols
