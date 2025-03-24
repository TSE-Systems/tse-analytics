from PySide6.QtWidgets import QWidget, QComboBox, QHBoxLayout

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.views.misc.factor_selector import FactorSelector


class SplitModeSelector(QWidget, messaging.MessengerListener):
    def __init__(self, parent: QWidget, datatable: Datatable, callback):
        super().__init__(parent)

        messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
        self.destroyed.connect(lambda: messaging.unsubscribe_all(self))

        self.datatable = datatable
        self.callback = callback

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.split_mode_combobox = QComboBox(self)

        self.split_modes = []
        self._set_available_split_modes(datatable.dataset.binning_settings.apply)
        self.split_mode_combobox.currentTextChanged.connect(self._split_mode_changed)
        layout.addWidget(self.split_mode_combobox)

        self.factorSelector = FactorSelector()
        items = list(datatable.dataset.factors.keys())
        self.factorSelector.addItems(items)
        self.factorSelector.setVisible(False)
        self.factorSelector.currentTextChanged.connect(self._factor_name_changed)
        layout.addWidget(self.factorSelector)

        self.setLayout(layout)

    def _on_binning_applied(self, message: messaging.BinningMessage):
        if message.dataset == self.datatable.dataset:
            self._set_available_split_modes(message.settings.apply)

    def _set_available_split_modes(self, binning_active: bool) -> None:
        split_modes = ["By animal"]
        if "Bin" in self.datatable.active_df.columns or binning_active:
            split_modes.append("Total")
            if self.datatable.get_merging_mode() is not None:
                split_modes.append("By run")
            # if "Run" in self.datatable.active_df.columns:
            #     split_modes.append("By run")
            if len(self.datatable.dataset.factors) > 0:
                split_modes.append("By factor")

        if split_modes != self.split_modes:
            # self.split_mode_combobox.blockSignals(True)
            self.split_mode_combobox.clear()
            self.split_mode_combobox.addItems(split_modes)
            # self.split_mode_combobox.blockSignals(False)
            self.split_modes = split_modes

    def update_split_modes(self, split_modes: list[str]) -> None:
        if split_modes != self.split_modes:
            # self.split_mode_combobox.blockSignals(True)
            self.split_mode_combobox.clear()
            self.split_mode_combobox.addItems(split_modes)
            # self.split_mode_combobox.blockSignals(False)
            self.split_modes = split_modes

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
            case "Total":
                return SplitMode.TOTAL
            case "By factor":
                return SplitMode.FACTOR
            case "By run":
                return SplitMode.RUN
            case _:
                return SplitMode.ANIMAL
