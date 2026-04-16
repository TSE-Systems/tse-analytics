from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QAbstractItemView, QAbstractScrollArea, QHeaderView, QTableView

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.data.shared import Animal
from tse_analytics.core.models.animals_simple_model import AnimalsSimpleModel
from tse_analytics.core.utils.ui import set_inactive_palette


class AnimalsTableView(QTableView):
    def __init__(self, dataset: Dataset, parent=None):
        super().__init__(
            parent,
            sortingEnabled=True,
        )

        self.dataset = dataset

        set_inactive_palette(self)

        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.horizontalHeader().ResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setMinimumSectionSize(20)
        self.verticalHeader().setDefaultSectionSize(20)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setModel(proxy_model)

        model = AnimalsSimpleModel(dataset)
        self.model().setSourceModel(model)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setMinimumWidth(self.horizontalHeader().length())

        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.resizeColumnsToContents()

    def get_selected_animal_ids(self) -> list[str]:
        selected_rows = self.selectionModel().selectedRows(column=0)
        return [index.data() for index in selected_rows]

    def get_selected_animals_dict(self) -> dict[str, Animal]:
        selected_rows = self.selectionModel().selectedRows(column=0)
        result = {}
        for index in selected_rows:
            animal_id = index.data()
            result[animal_id] = self.dataset.animals[animal_id]
        return result
