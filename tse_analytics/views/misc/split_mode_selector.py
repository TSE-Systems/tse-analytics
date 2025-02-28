from PySide6.QtWidgets import QWidget, QComboBox, QHBoxLayout

from tse_analytics.core.data.shared import Factor, SplitMode
from tse_analytics.views.misc.factor_selector import FactorSelector


class SplitModeSelector(QWidget):
    def __init__(self, parent: QWidget, factors: dict[str, Factor], callback):
        super().__init__(parent)

        self.callback = callback

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.split_mode_combobox = QComboBox(self)
        split_modes = (
            ["By animal", "By factor", "By run", "Total"] if len(factors) > 0 else ["By animal", "By run", "Total"]
        )
        self.split_mode_combobox.addItems(split_modes)
        self.split_mode_combobox.currentTextChanged.connect(self._split_mode_changed)
        layout.addWidget(self.split_mode_combobox)

        self.factorSelector = FactorSelector()
        items = list(factors.keys())
        self.factorSelector.addItems(items)
        self.factorSelector.setVisible(False)
        self.factorSelector.currentTextChanged.connect(self._factor_name_changed)
        layout.addWidget(self.factorSelector)

        self.setLayout(layout)

    def _split_mode_changed(self, mode: str) -> None:
        self.factorSelector.setVisible(mode == "By factor")
        self._call_callback()

    def _factor_name_changed(self, factor_name: str) -> None:
        self._call_callback()

    def _call_callback(self) -> None:
        split_mode = self._get_split_mode()
        factor_name = self.factorSelector.currentText()
        self.callback(split_mode, factor_name)

    def _get_split_mode(self) -> SplitMode:
        match self.split_mode_combobox.currentText():
            case "By animal":
                return SplitMode.ANIMAL
            case "By factor":
                return SplitMode.FACTOR
            case "By run":
                return SplitMode.RUN
            case "Total":
                return SplitMode.TOTAL
