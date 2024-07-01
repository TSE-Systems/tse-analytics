from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt, QTimer
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QAbstractItemView, QTableView, QWidget

from tse_analytics.modules.phenomaster.actimot.data.actimot_animal_item import ActimotAnimalItem
from tse_analytics.modules.phenomaster.actimot.models.actimot_boxes_model import ActimotBoxesModel
from tse_analytics.modules.phenomaster.data.dataset import Dataset


class ActimotBoxSelector(QTableView):
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

    def set_data(self, dataset: Dataset):
        items: dict[str, ActimotAnimalItem] = {}
        for animal in dataset.animals.values():
            items[animal.id] = ActimotAnimalItem(animal.box, animal.id, {})
        animal_ids = list(items.keys())

        header = ["Animal", "Box"]
        for factor in dataset.factors.values():
            header.append(factor.name)
            for animal_id in animal_ids:
                x = items[animal_id]
                x.factors[factor.name] = None
                for group in factor.groups:
                    if animal_id in group.animal_ids:
                        x.factors[factor.name] = group.name
                        break

        model = ActimotBoxesModel(list(items.values()), header)
        self.model().setSourceModel(model)
        # See https://forum.pythonguis.com/t/resizecolumnstocontents-not-working-with-qsortfilterproxymodel-and-tableview/1285
        QTimer.singleShot(0, self.resizeColumnsToContents)

    def __on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model = self.model()
        model = proxy_model.sourceModel()
        selected_boxes: list[ActimotAnimalItem] = []
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                box = model.items[row]
                selected_boxes.append(box)
        self.callback(selected_boxes)
