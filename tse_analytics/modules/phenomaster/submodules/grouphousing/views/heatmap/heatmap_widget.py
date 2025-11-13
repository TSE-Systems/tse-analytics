import pandas as pd
import seaborn as sns
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.submodules.grouphousing.data.grouphousing_data import GroupHousingData
from tse_analytics.modules.phenomaster.submodules.grouphousing.views.heatmap.heatmap_widget_ui import (
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
        self.ui.listWidgetAnimals.setCurrentRow(0)

    def set_preprocessed_data(self, preprocessed_data: dict[str, pd.DataFrame]):
        self.preprocessed_data = preprocessed_data
        self._set_data()

    def _animals_selection_changed(self):
        self.selected_animals = [item.text() for item in self.ui.listWidgetAnimals.selectedItems()]
        self._set_data()

    def _set_data(self) -> None:
        if self.preprocessed_data is None or len(self.selected_animals) == 0:
            return

        df = self.preprocessed_data["All"]
        df = df[df["Animal"].isin(self.selected_animals)]
        df["Hour"] = df["StartDateTime"].dt.hour

        grouped = df.groupby(["ChannelType", df["Hour"]], observed=False).aggregate(
            Count=("Activity", "count"),
        )
        grouped.sort_values(["Hour", "ChannelType"], inplace=True)
        grouped.reset_index(inplace=True)

        grid = grouped.pivot(index="ChannelType", columns="Hour", values="Count")
        if grid.empty:
            return

        self.ui.canvas.clear(False)
        ax = self.ui.canvas.figure.add_subplot(111)

        sns.heatmap(
            grid,
            fmt="g",
            annot=True,
            linewidth=0.5,
            ax=ax,
        )
        ax.set_title("Antennas Registrations")

        self.ui.canvas.figure.tight_layout()
        self.ui.canvas.draw()
