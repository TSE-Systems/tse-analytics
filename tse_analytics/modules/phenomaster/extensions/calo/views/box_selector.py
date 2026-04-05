from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QAbstractItemView, QTableView, QWidget

from tse_analytics.core.data.dataset import Dataset
from tse_analytics.core.utils.ui import set_inactive_palette
from tse_analytics.modules.phenomaster.extensions.calo.data.calo_box import CaloBox
from tse_analytics.modules.phenomaster.extensions.calo.data.calo_boxes_model import CaloBoxesModel
from tse_analytics.modules.phenomaster.io.tse_import_settings import CALO_BIN_TABLE


class BoxSelector(QTableView):
    def __init__(self, callback, parent: QWidget | None = None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(20)

        self.callback = callback

        set_inactive_palette(self)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setModel(proxy_model)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def set_data(self, dataset: Dataset):
        all_box_numbers = dataset.raw_datatables["Calo"][CALO_BIN_TABLE].df["Box"].unique().tolist()
        boxes: list[CaloBox] = []

        for box in all_box_numbers:
            ref_box = dataset.raw_datatables["Calo"][CALO_BIN_TABLE].metadata["ref_box_mapping"].get(box, None)
            if ref_box is not None:
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
