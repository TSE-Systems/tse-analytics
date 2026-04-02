from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt
from PySide6.QtWidgets import QAbstractItemView, QTableView, QWidget

from tse_analytics.core.models.bins_model import BinsModel
from tse_analytics.core.utils.ui import set_inactive_palette
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


class BinSelector(QTableView):
    def __init__(self, callback, parent: QWidget | None = None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(20)

        self.callback = callback

        set_inactive_palette(self)

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setModel(proxy_model)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def set_data(self, dataset: PhenoMasterDataset):
        bins = list(dataset.calo_data.raw_datatable.df["Bin"].unique())
        model = BinsModel(bins)
        self.model().setSourceModel(model)
        # self.resizeColumnsToContents()

    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model = self.model()
        model = proxy_model.sourceModel()
        selected_bins: list[int] = []
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                box = model.items[row]
                selected_bins.append(box)
        self.callback(selected_bins)
