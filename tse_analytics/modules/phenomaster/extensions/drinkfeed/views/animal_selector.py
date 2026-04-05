from functools import partial

import pandas as pd
from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt, QTimer
from PySide6.QtWidgets import QAbstractItemView, QMenu, QTableView, QWidget

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.utils.ui import set_inactive_palette
from tse_analytics.modules.phenomaster.extensions.drinkfeed.data.drinkfeed_animal_item import DrinkFeedAnimalItem
from tse_analytics.modules.phenomaster.extensions.drinkfeed.data.drinkfeed_animals_model import (
    DrinkFeedAnimalsModel,
)


class AnimalSelector(QTableView):
    def __init__(self, callback, settings_widget, parent: QWidget | None = None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(20)

        self.callback = callback
        self.settings_widget = settings_widget

        set_inactive_palette(self)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setModel(proxy_model)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)

    def set_data(self, dataset: Dataset):
        items: dict[str, DrinkFeedAnimalItem] = {}
        for animal in dataset.animals.values():
            items[animal.id] = DrinkFeedAnimalItem(animal.properties["Box"], animal.id, pd.NA, {})
        animal_ids = list(items.keys())

        header = ["Animal", "Box", "Diet"]
        for factor in dataset.factors.values():
            header.append(factor.name)
            for animal_id in animal_ids:
                x = items[animal_id]
                x.factors[factor.name] = None
                for level in factor.levels:
                    if animal_id in level.animal_ids:
                        x.factors[factor.name] = level.name
                        break

        model = DrinkFeedAnimalsModel(list(items.values()), header)
        self.model().setSourceModel(model)
        # See https://forum.pythonguis.com/t/resizecolumnstocontents-not-working-with-qsortfilterproxymodel-and-tableview/1285
        QTimer.singleShot(0, self.resizeColumnsToContents)

    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model = self.model()
        model = proxy_model.sourceModel()
        selected_animals: list[DrinkFeedAnimalItem] = []
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                animal = model.items[row]
                selected_animals.append(animal)
        self.callback(selected_animals)

    def _open_context_menu(self, position):
        menu = QMenu(self)

        action = menu.addAction("Clear diets")
        action.triggered.connect(self._clear_diets)

        submenu = menu.addMenu("Set diet")
        settings = self.settings_widget.get_drinkfeed_settings()
        for diet in settings.diets:
            action = submenu.addAction(diet.name)
            action.triggered.connect(partial(self._set_diet, diet.caloric_value))

        menu.exec_(self.viewport().mapToGlobal(position))

    def _clear_diets(self):
        indexes = [self.model().mapToSource(index) for index in self.selectedIndexes()]
        self.model().sourceModel().clear_diets(indexes)

    def _set_diet(self, caloric_value: float):
        indexes = [self.model().mapToSource(index) for index in self.selectedIndexes()]
        self.model().sourceModel().set_diet(indexes, caloric_value)

    def get_diets_dict(self) -> dict[str, float]:
        return self.model().sourceModel().get_diets_dict()
