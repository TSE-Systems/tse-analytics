from PySide6.QtWidgets import QWidget, QComboBox

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode


class GroupBySelector(QComboBox, messaging.MessengerListener):
    def __init__(self, parent: QWidget, datatable: Datatable, callback):
        super().__init__(parent)

        self.setMinimumWidth(80)

        messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
        self.destroyed.connect(lambda: messaging.unsubscribe_all(self))

        self.datatable = datatable
        self.callback = callback

        self.modes = []
        self._set_available_modes()

        self.currentTextChanged.connect(self._mode_changed)

    def showPopup(self):
        self._set_available_modes()
        super().showPopup()

    def _on_binning_applied(self, message: messaging.BinningMessage):
        if message.dataset == self.datatable.dataset:
            self._set_available_modes()

    def _set_available_modes(self) -> None:
        modes = self.datatable.get_group_by_columns()
        if modes != self.modes:
            self.blockSignals(True)
            self.clear()
            self.blockSignals(False)
            self.addItems(modes)
            self.modes = modes

    def _mode_changed(self, mode: str) -> None:
        split_mode = self._get_split_mode()
        factor_name = self.currentText()
        self.callback(split_mode, factor_name)

    def _get_split_mode(self) -> SplitMode:
        mode_text = self.currentText()
        match mode_text:
            case "Animal":
                return SplitMode.ANIMAL
            case "Total":
                return SplitMode.TOTAL
            case "Run":
                return SplitMode.RUN
            case _:
                if mode_text in self.datatable.dataset.factors.keys():
                    return SplitMode.FACTOR
                else:
                    return SplitMode.ANIMAL
