from PySide6.QtWidgets import QComboBox, QWidget

from tse_analytics.core import messaging
from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings


class GroupBySelector(QComboBox, messaging.MessengerListener):
    def __init__(
        self,
        parent: QWidget,
        datatable: Datatable,
        check_binning=False,
        selected_mode: str = None,
        disable_total_mode: bool = False,
    ):
        super().__init__(parent)

        self.setMinimumWidth(80)

        self.datatable = datatable
        self.check_binning = check_binning
        self.disable_total_mode = disable_total_mode
        self.modes = []

        if check_binning:
            messaging.subscribe(self, messaging.BinningMessage, self._on_binning_applied)
            self.destroyed.connect(lambda: messaging.unsubscribe_all(self))

        self._set_available_modes()

        if selected_mode is not None:
            self.setCurrentText(selected_mode)

    def get_grouping_settings(self) -> GroupingSettings:
        mode_text = self.currentText()
        factor_name = ""
        match mode_text:
            case "Animal":
                grouping_mode = GroupingMode.ANIMAL
            case "Total":
                grouping_mode = GroupingMode.TOTAL
            case "Run":
                grouping_mode = GroupingMode.RUN
            case _:
                if mode_text in self.datatable.dataset.factors.keys():
                    grouping_mode = GroupingMode.FACTOR
                    factor_name = mode_text
                else:
                    grouping_mode = GroupingMode.ANIMAL
        return GroupingSettings(mode=grouping_mode, factor_name=factor_name)

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
        modes = self.datatable.get_group_by_columns(self.check_binning, disable_total_mode=self.disable_total_mode)
        if modes != self.modes:
            self.blockSignals(True)
            self.clear()
            self.blockSignals(False)
            self.addItems(modes)
            self.modes = modes
