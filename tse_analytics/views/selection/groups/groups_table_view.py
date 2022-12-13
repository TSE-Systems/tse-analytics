from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QHeaderView, QTableView

from tse_analytics.core.manager import Manager
from tse_analytics.models.groups_model import GroupsModel
from tse_datatools.data.group import Group


class GroupsTableView(QTableView):
    def __init__(self, parent):
        super().__init__(parent)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setModel(proxy_model)
        self.horizontalHeader().ResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setDefaultSectionSize(10)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setEditTriggers(QTableView.NoEditTriggers)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setSortingEnabled(True)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def clear(self):
        self.model().setSourceModel(None)

    def set_data(self, groups: dict[str, Group]):
        model = GroupsModel(list(groups.values()))
        self.model().setSourceModel(model)

    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model: QSortFilterProxyModel = self.model()
        model = proxy_model.sourceModel()
        selected_groups: list[Group] = []
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                group = model.items[row]
                selected_groups.append(group)
        Manager.data.set_selected_groups(selected_groups)
