from PySide6.QtCore import QItemSelection, QSortFilterProxyModel, Qt, QTimer
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QAbstractItemView, QTableView, QWidget

from tse_analytics.modules.phenomaster.submodules.actimot.data.actimot_animal_item import ActimotAnimalItem
from tse_analytics.modules.phenomaster.submodules.actimot.models.actimot_boxes_model import ActimotBoxesModel
from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset


class ActimotBoxSelector(QTableView):
    def __init__(self, callback, settings_widget, parent: QWidget | None = None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        self.verticalHeader().setDefaultSectionSize(20)

        self.callback = callback
        self.settings_widget = settings_widget

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
        items: dict[str, ActimotAnimalItem] = {}
        for animal in dataset.animals.values():
            items[animal.id] = ActimotAnimalItem(animal.properties["Box"], animal.id, {})
        animal_ids = list(items.keys())

        header = ["Animal", "Box"]
        for factor in dataset.factors.values():
            header.append(factor.name)
            for animal_id in animal_ids:
                x = items[animal_id]
                x.factors[factor.name] = None
                for level in factor.levels:
                    if animal_id in level.animal_ids:
                        x.factors[factor.name] = level.name
                        break

        model = ActimotBoxesModel(list(items.values()), header)
        self.model().setSourceModel(model)
        # See https://forum.pythonguis.com/t/resizecolumnstocontents-not-working-with-qsortfilterproxymodel-and-tableview/1285
        QTimer.singleShot(0, self.resizeColumnsToContents)

    def _on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        proxy_model = self.model()
        model = proxy_model.sourceModel()
        selected_box: ActimotAnimalItem = None
        for index in self.selectedIndexes():
            if index.column() != 0:
                continue
            if index.isValid():
                source_index = proxy_model.mapToSource(index)
                row = source_index.row()
                box = model.items[row]
                selected_box = box
        self.callback(selected_box)
