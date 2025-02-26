import seaborn as sns
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.data.phenomaster_dataset import PhenoMasterDataset
from tse_analytics.modules.phenomaster.submodules.trafficage.views.trafficage_heatmap_widget_ui import (
    Ui_TraffiCageHeatmapWidget,
)


class TraffiCageHeatmapWidget(QWidget):
    def __init__(self, dataset: PhenoMasterDataset, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_TraffiCageHeatmapWidget()
        self.ui.setupUi(self)

        self.dataset = dataset

        animal_ids = list(self.dataset.animals.keys())
        animal_ids.sort()
        self.ui.listWidgetAnimals.addItems(animal_ids)
        self.ui.listWidgetAnimals.itemSelectionChanged.connect(self._animals_selection_changed)

        self.df = self.dataset.trafficage_data.df
        self.selected_animals: list[str] = []

    def _animals_selection_changed(self):
        self.selected_animals = [item.text() for item in self.ui.listWidgetAnimals.selectedItems()]
        self._set_data()

    def _set_data(self) -> None:
        df = self.df
        if len(self.selected_animals) > 0:
            df = df[df["Animal"].isin(self.selected_animals)]

        grouped = df.groupby("ChannelType").aggregate(
            Count=("Activity", "count"),
        )

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        sns.heatmap(
            grouped,
            fmt="g",
            annot=True,
            linewidth=0.5,
            ax=ax,
        )

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
