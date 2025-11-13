from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QAbstractItemView, QTableView, QWidget

from tse_analytics.modules.phenomaster.submodules.calo.data.calo_box import CaloBox, get_ref_box_number
from tse_analytics.modules.phenomaster.submodules.calo.models.calo_boxes_model import CaloBoxesModel
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


class BoxSelector(QTableView):
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
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def set_data(self, dataset: PhenoMasterDataset):
        all_box_numbers = list(dataset.calo_data.raw_df["Box"].unique())
        boxes: list[CaloBox] = []

        for box in all_box_numbers:
            ref_box = get_ref_box_number(box, all_box_numbers)
            boxes.append(CaloBox(box, ref_box))
        model = CaloBoxesModel(boxes)
        self.model().setSourceModel(model)
        # self.resizeColumnsToContents()

    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model = self.model()
        model = proxy_model.sourceModel()
        selected_boxes: list[CaloBox] = []
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                box = model.items[row]
                selected_boxes.append(box)
        self.callback(selected_boxes)
