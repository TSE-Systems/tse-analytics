from PySide6.QtCore import QSortFilterProxyModel, QItemSelection, Qt
from PySide6.QtWidgets import QTableView, QHeaderView
from tse_datatools.data.animal import Animal

from tse_analytics.core.manager import Manager
from tse_analytics.messaging.messages import SelectedAnimalsChangedMessage
from tse_analytics.models.animals_model import AnimalsModel


class AnimalsTableView(QTableView):
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

    def set_data(self, animals: dict[int, Animal]):
        model = AnimalsModel(list(animals.values()))
        self.model().setSourceModel(model)

    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model: QSortFilterProxyModel = self.model()
        model = proxy_model.sourceModel()
        selected_animals: list[Animal] = []
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                animal = model.items[row]
                selected_animals.append(animal)
        Manager.messenger.broadcast(SelectedAnimalsChangedMessage(self, selected_animals))