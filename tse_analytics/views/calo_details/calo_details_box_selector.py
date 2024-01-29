from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QAbstractItemView, QTableView, QWidget
from tse_datatools.data.calo_details_box import CaloDetailsBox, get_ref_box_number
from tse_datatools.data.dataset import Dataset

from tse_analytics.models.calo_details_boxes_model import CaloDetailsBoxesModel


class CaloDetailsBoxSelector(QTableView):
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
        all_box_numbers = list(dataset.calo_details.raw_df["Box"].unique())
        boxes: list[CaloDetailsBox] = []
        for box in all_box_numbers:
            ref_box = get_ref_box_number(box, all_box_numbers)
            boxes.append(CaloDetailsBox(box, ref_box))
        model = CaloDetailsBoxesModel(boxes)
        self.model().setSourceModel(model)
        # self.resizeColumnsToContents()

    def __on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model = self.model()
        model = proxy_model.sourceModel()
        selected_boxes: list[CaloDetailsBox] = []
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                box = model.items[row]
                selected_boxes.append(box)
        self.callback(selected_boxes)
