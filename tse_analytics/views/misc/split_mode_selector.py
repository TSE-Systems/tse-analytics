from PySide6.QtWidgets import QComboBox, QHBoxLayout, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode
from tse_analytics.views.misc.factor_selector import FactorSelector


class SplitModeSelector(QWidget, messaging.MessengerListener):
    """
    A widget for selecting how to split data for analysis.

    This widget provides a combo box for selecting the split mode (by animal, total,
    by run, or by factor) and a factor selector that appears when "By factor" is selected.
    It listens for binning messages to update available split modes when binning changes.
    """

    def __init__(self, parent: QWidget, datatable: Datatable, callback):
        """
        Initialize the SplitModeSelector widget.

        Args:
            parent: The parent widget.
            datatable: The Datatable object containing the data to be split.
            callback: Function to call when the split mode selection changes.
                     The function should accept split_mode and factor_name parameters.
        """
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
        """
        Handle binning messages from the messaging system.

        This method is called when binning is applied to a dataset. If the binning
        was applied to the current dataset, it updates the available split modes.

        Args:
            message: The BinningMessage containing information about the binning operation.
        """
        if message.dataset == self.datatable.dataset:
            self._set_available_split_modes(message.settings.apply)

    def _set_available_split_modes(self, binning_active: bool) -> None:
        """
        Update the available split modes based on the current data and binning status.

        This method determines which split modes are available based on the current
        datatable state and binning settings, then updates the combo box accordingly.

        Args:
            binning_active: Whether binning is currently active for the dataset.
        """
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

    def _split_mode_changed(self, mode: str) -> None:
        """
        Handle changes to the selected split mode.

        This method is called when the user selects a different split mode.
        It shows or hides the factor selector based on the selected mode
        and calls the callback function with the new selection.

        Args:
            mode: The text of the newly selected mode.
        """
        self.factorSelector.setVisible(mode == "By factor")
        self._call_callback()

    def _factor_name_changed(self, factor_name: str) -> None:
        """
        Handle changes to the selected factor.

        This method is called when the user selects a different factor in the factor selector.
        It calls the callback function with the new selection.

        Args:
            factor_name: The name of the newly selected factor.
        """
        self._call_callback()

    def _call_callback(self) -> None:
        """
        Call the callback function with the current selection.

        This method gets the current split mode and factor name and passes them
        to the callback function provided during initialization.
        """
        split_mode = self._get_split_mode()
        factor_name = self.factorSelector.currentText()
        self.callback(split_mode, factor_name)

    def _get_split_mode(self) -> SplitMode:
        """
        Convert the current text selection to a SplitMode enum value.

        Returns:
            The appropriate SplitMode enum value for the current selection.
        """
        match self.split_mode_combobox.currentText():
            case "Total":
                return SplitMode.TOTAL
            case "By factor":
                return SplitMode.FACTOR
            case "By run":
                return SplitMode.RUN
            case _:
                return SplitMode.ANIMAL
