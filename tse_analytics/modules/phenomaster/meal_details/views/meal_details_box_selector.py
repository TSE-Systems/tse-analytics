from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QAbstractItemView, QTableView, QWidget

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.modules.phenomaster.meal_details.models.meal_details_boxes_model import MealDetailsBoxesModel
from tse_analytics.modules.phenomaster.meal_details.data.meal_details_box import MealDetailsBox


class MealDetailsBoxSelector(QTableView):
    def __init__(self, callback, parent: QWidget | None = None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(20)

        self.callback = callback

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
        box_to_animal_map = {}
        for animal in dataset.animals.values():
            box_to_animal_map[animal.box] = animal.id

        all_box_numbers = list(dataset.meal_details.raw_df["Box"].unique())
        boxes: list[MealDetailsBox] = []
        for box in all_box_numbers:
            boxes.append(MealDetailsBox(box, box_to_animal_map[box]))
        model = MealDetailsBoxesModel(boxes)
        self.model().setSourceModel(model)
        # self.resizeColumnsToContents()

    def __on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model = self.model()
        model = proxy_model.sourceModel()
        selected_boxes: list[MealDetailsBox] = []
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                box = model.items[row]
                selected_boxes.append(box)
        self.callback(selected_boxes)
