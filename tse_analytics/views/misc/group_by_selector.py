from PySide6.QtWidgets import QWidget, QComboBox

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import SplitMode


class GroupBySelector(QComboBox, messaging.MessengerListener):
    """
    A combo box widget for selecting how to group data.

    This widget allows users to select different ways to group data for analysis,
    such as by animal, by factor, by run, or as a total. It dynamically updates
    available options based on the current dataset and binning settings.
    """

    def __init__(self, parent: QWidget, datatable: Datatable, callback=None, check_binning=True):
        """
        Initialize the GroupBySelector widget.

        Args:
            parent: The parent widget.
            datatable: The Datatable object containing the data to be grouped.
            callback: Optional function to call when the grouping selection changes.
                     The function should accept split_mode and selected_factor_name parameters.
            check_binning: If True, considers binning when determining available grouping options.
                          Default is True.
        """
        super().__init__(parent)

        self.setMinimumWidth(80)

        messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
        self.destroyed.connect(lambda: messaging.unsubscribe_all(self))

        self.datatable = datatable
        self.callback = callback
        self.check_binning = check_binning

        self.modes = []
        self._set_available_modes()

        self.currentTextChanged.connect(self._mode_changed)

    def get_group_by(self) -> tuple[SplitMode, str]:
        """
        Get the current grouping selection.

        Returns:
            A tuple containing the selected SplitMode and the factor name (if applicable).
            If the split mode is not FACTOR, the factor name will be an empty string.
        """
        split_mode = self._get_split_mode()
        if split_mode == SplitMode.FACTOR:
            return split_mode, self.currentText()
        else:
            return split_mode, ""

    def showPopup(self):
        """
        Override the showPopup method to update available modes before showing the dropdown.

        This ensures that the list of available grouping options is always up-to-date
        when the user clicks on the combo box.
        """
        self._set_available_modes()
        super().showPopup()

    def _on_binning_applied(self, message: messaging.BinningMessage):
        """
        Handle binning messages from the messaging system.

        This method is called when binning is applied to a dataset. If the binning
        was applied to the current dataset, it updates the available grouping options.

        Args:
            message: The BinningMessage containing information about the binning operation.
        """
        if message.dataset == self.datatable.dataset:
            self._set_available_modes()

    def _set_available_modes(self) -> None:
        """
        Update the available grouping options in the combo box.

        This method retrieves the current available grouping options from the datatable
        and updates the combo box items if they have changed.
        """
        modes = self.datatable.get_group_by_columns(self.check_binning)
        if modes != self.modes:
            self.blockSignals(True)
            self.clear()
            self.blockSignals(False)
            self.addItems(modes)
            self.modes = modes

    def _mode_changed(self, mode: str) -> None:
        """
        Handle changes to the selected grouping mode.

        This method is called when the user selects a different grouping option.
        If a callback function was provided, it calls that function with the new selection.

        Args:
            mode: The text of the newly selected mode.
        """
        if self.callback is not None:
            split_mode, selected_factor_name = self.get_group_by()
            self.callback(split_mode, selected_factor_name)

    def _get_split_mode(self) -> SplitMode:
        """
        Determine the SplitMode enum value based on the current text selection.

        Returns:
            The appropriate SplitMode enum value for the current selection.
        """
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
