from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QComboBox, QToolBar, QVBoxLayout, QWidget

from tse_analytics.modules.phenomaster.extensions.calo.fitting_result import FittingResult
from tse_analytics.views.misc.MplCanvas import MplCanvas


class RerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = MplCanvas(self)

        # Setup toolbar
        toolbar = QToolBar(
            "Toolbar",
            iconSize=QSize(16, 16),
            toolButtonStyle=Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.comboBoxVariable = QComboBox()
        self.comboBoxVariable.addItems(["RER", "O2", "Ref.O2", "CO2", "Ref.CO2", "VO2", "VCO2", "EE"])
        self.comboBoxVariable.currentTextChanged.connect(self._variable_changed)
        toolbar.addWidget(self.comboBoxVariable)

        plot_toolbar = NavigationToolbar2QT(self.canvas, self)
        plot_toolbar.setIconSize(QSize(16, 16))
        toolbar.addWidget(plot_toolbar)

        # Insert the toolbar to the widget
        self._layout.addWidget(toolbar)

        self._layout.addWidget(self.canvas)

        self.fitting_result: FittingResult | None = None

    def _variable_changed(self, variable: str) -> None:
        self.set_data(self.fitting_result)

    def clear(self) -> None:
        self.canvas.clear(True)

    def set_data(self, fitting_result: FittingResult) -> None:
        self.fitting_result = fitting_result

        if self.fitting_result is None:
            return

        self.canvas.clear(False)
        ax = self.canvas.figure.add_subplot(111)

        variable = self.comboBoxVariable.currentText()

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

        self.canvas.figure.tight_layout()
        self.canvas.draw()
