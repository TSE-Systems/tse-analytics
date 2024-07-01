from functools import partial

import pandas as pd
from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt, QTimer
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QAbstractItemView, QMenu, QTableView, QWidget

from tse_analytics.modules.phenomaster.data.dataset import Dataset
from tse_analytics.modules.phenomaster.meal_details.data.meal_details_animal_item import MealDetailsAnimalItem
from tse_analytics.modules.phenomaster.meal_details.models.meal_details_boxes_model import MealDetailsBoxesModel


class MealDetailsBoxSelector(QTableView):
    def __init__(self, callback, meal_details_settings_widget, parent: QWidget | None = None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(20)

        self.callback = callback
        self.meal_details_settings_widget = meal_details_settings_widget

        pal = self.palette()
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.Highlight,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight),
        )
        pal.setColor(
            QPalette.ColorGroup.Inactive,
            QPalette.ColorRole.HighlightedText,
            pal.color(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText),
        )
        self.setPalette(pal)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setModel(proxy_model)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.selectionModel().selectionChanged.connect(self.__on_selection_changed)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__open_context_menu)

    def set_data(self, dataset: Dataset):
        items: dict[str, MealDetailsAnimalItem] = {}
        for animal in dataset.animals.values():
            items[animal.id] = MealDetailsAnimalItem(animal.box, animal.id, pd.NA, {})
        animal_ids = list(items.keys())

        header = ["Animal", "Box", "Diet"]
        for factor in dataset.factors.values():
            header.append(factor.name)
            for animal_id in animal_ids:
                x = items[animal_id]
                x.factors[factor.name] = None
                for group in factor.groups:
                    if animal_id in group.animal_ids:
                        x.factors[factor.name] = group.name
                        break

        model = MealDetailsBoxesModel(list(items.values()), header)
        self.model().setSourceModel(model)
        # See https://forum.pythonguis.com/t/resizecolumnstocontents-not-working-with-qsortfilterproxymodel-and-tableview/1285
        QTimer.singleShot(0, self.resizeColumnsToContents)

    def __on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model = self.model()
        model = proxy_model.sourceModel()
        selected_boxes: list[MealDetailsAnimalItem] = []
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                box = model.items[row]
                selected_boxes.append(box)
        self.callback(selected_boxes)

    def __open_context_menu(self, position):
        menu = QMenu(self)

        action = menu.addAction("Clear diets")
        action.triggered.connect(self.__clear_diets)

        submenu = menu.addMenu("Set diet")
        settings = self.meal_details_settings_widget.get_meal_details_settings()
        for diet in settings.diets:
            action = submenu.addAction(diet.name)
            action.triggered.connect(partial(self.__set_diet, diet.caloric_value))

        menu.exec_(self.viewport().mapToGlobal(position))

    def __clear_diets(self):
        indexes = [self.model().mapToSource(index) for index in self.selectedIndexes()]
        self.model().sourceModel().clear_diets(indexes)

    def __set_diet(self, caloric_value: float):
        indexes = [self.model().mapToSource(index) for index in self.selectedIndexes()]
        self.model().sourceModel().set_diet(indexes, caloric_value)

    def get_diets_dict(self) -> dict[str, float]:
        return self.model().sourceModel().get_diets_dict()
