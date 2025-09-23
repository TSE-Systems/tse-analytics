import pandas as pd
import seaborn as sns
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.submodules.grouphousing.data.grouphousing_data import GroupHousingData
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.heatmap_widget.heatmap_widget_ui import (
    Ui_HeatmapWidget,
)


class HeatmapWidget(QWidget):
    def __init__(self, data: GroupHousingData, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_HeatmapWidget()
        self.ui.setupUi(self)

        self.data = data
        self.preprocessed_data: dict[str, pd.DataFrame] | None = None
        self.selected_animals: list[str] = []

        self.ui.listWidgetAnimals.addItems(self.data.animal_ids)
        self.ui.listWidgetAnimals.itemSelectionChanged.connect(self._animals_selection_changed)

    def set_preprocessed_data(self, preprocessed_data: dict[str, pd.DataFrame]):
        self.preprocessed_data = preprocessed_data
        self._set_data()

    def _animals_selection_changed(self):
        self.selected_animals = [item.text() for item in self.ui.listWidgetAnimals.selectedItems()]
        self._set_data()

    def _set_data(self) -> None:
        df = self.preprocessed_data["All"]
        if len(self.selected_animals) > 0:
            df = df[df["Animal"].isin(self.selected_animals)]

        grouped = df.groupby("ChannelType", observed=True).aggregate(
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
