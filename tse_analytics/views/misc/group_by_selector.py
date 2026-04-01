from PySide6.QtWidgets import QComboBox, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.grouping import GroupingMode, GroupingSettings


class GroupBySelector(QComboBox):
    def __init__(
        self,
        parent: QWidget,
        datatable: Datatable,
        selected_mode: str = None,
        disable_total_mode: bool = False,
        disable_run_mode: bool = False,
        disable_animal_mode: bool = False,
    ):
        super().__init__(parent)

        self.setMinimumWidth(80)
        self.datatable = datatable

        modes = self.datatable.get_group_by_columns(
            check_binning=False,
            disable_total_mode=disable_total_mode,
            disable_run_mode=disable_run_mode,
            disable_animal_mode=disable_animal_mode,
        )
        self.addItems(modes)

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
