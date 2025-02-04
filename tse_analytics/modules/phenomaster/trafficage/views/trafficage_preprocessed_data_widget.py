import pandas as pd
from PySide6.QtWidgets import QWidget

from tse_analytics.core.models.pandas_simple_model import PandasSimpleModel
from tse_analytics.modules.phenomaster.data.pm_dataset import PMDataset
from tse_analytics.modules.phenomaster.trafficage.views.trafficage_preprocessed_data_widget_ui import \
    Ui_TraffiCagePreprocessedDataWidget


class TraffiCagePreprocessedDataWidget(QWidget):
    def __init__(self, dataset: PMDataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_TraffiCagePreprocessedDataWidget()
        self.ui.setupUi(self)

        self.dataset = dataset

        self.ui.listWidgetTables.addItems([
            "Records",
        ])
        self.ui.listWidgetTables.itemSelectionChanged.connect(self._table_selection_changed)

        animal_ids = list(self.dataset.animals.keys())
        animal_ids.sort()
        self.ui.listWidgetAnimals.addItems(animal_ids)
        self.ui.listWidgetAnimals.itemSelectionChanged.connect(self._animals_selection_changed)

        self.df: pd.DataFrame | None = None
        self.selected_animals: list[str] = []

        self.ui.listWidgetTables.setCurrentRow(0)

    def _table_selection_changed(self):
        selected_table = self.ui.listWidgetTables.selectedItems()[0].text()
        match selected_table:
            case "Records":
                self.df = self.dataset.trafficage_data.df
            case _:
                self.df = self.dataset.trafficage_data.df
        self._set_data()
        self.ui.tableView.resizeColumnsToContents()

    def _animals_selection_changed(self):
        self.selected_animals = [item.text() for item in self.ui.listWidgetAnimals.selectedItems()]
        self._set_data()

    def _set_data(self) -> None:
        df = self.df
        if len(self.selected_animals) > 0:
            df = df[df["Animal"].isin(self.selected_animals)]
        model = PandasSimpleModel(df)
        self.ui.tableView.setModel(model)
