from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.calo_details.calo_details_fitting_result import CaloDetailsFittingResult
from tse_analytics.modules.phenomaster.calo_details.views.calo_details_rer_widget_ui import Ui_CaloDetailsRerWidget


class CaloDetailsRerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_CaloDetailsRerWidget()
        self.ui.setupUi(self)

        self.ui.comboBoxVariable.addItems(["RER", "O2", "Ref.O2", "CO2", "Ref.CO2", "VO2(3)", "VCO2(3)", "H(3)"])
        self.ui.comboBoxVariable.currentTextChanged.connect(self._variable_changed)

        self.ui.horizontalLayout.insertWidget(
            self.ui.horizontalLayout.count(), NavigationToolbar2QT(self.ui.canvas, self)
        )

        self.fitting_result: CaloDetailsFittingResult | None = None

    def _variable_changed(self, variable: str) -> None:
        self.set_data(self.fitting_result)

    def clear(self) -> None:
        self.ui.canvas.clear(True)

    def set_data(self, fitting_result: CaloDetailsFittingResult) -> None:
        self.fitting_result = fitting_result

        if self.fitting_result is None:
            return

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        variable = self.ui.comboBoxVariable.currentText()

        self.fitting_result.df.plot(
            x="Bin",
            y=f"{variable}",
            kind="line",
            title=f"{variable} [Box {self.fitting_result.box_number}]",
            label="Measured",
            ax=ax,
        )
        self.fitting_result.df.plot(
            x="Bin",
            y=f"{variable}-p",
            kind="line",
            label="Predicted",
            ax=ax,
        )

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
