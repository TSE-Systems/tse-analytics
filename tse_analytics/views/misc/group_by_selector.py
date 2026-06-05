from PySide6.QtWidgets import QComboBox, QWidget

from tse_analytics.core.data.datatable import Datatable
from tse_analytics.core.data.shared import FactorRole


class GroupBySelector(QComboBox):
    def __init__(
        self,
        parent: QWidget,
        datatable: Datatable,
        selected_mode: str = None,
        show_role: FactorRole | None = None,
    ):
        super().__init__(parent)

        self.setMinimumWidth(80)
        self.datatable = datatable

        modes = self.datatable.get_group_by_columns(
            show_role=show_role,
        )
        self.addItems(modes)

        if selected_mode is not None:
            self.setCurrentText(selected_mode)
