import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.actimot.actimot_processor import get_pixmap_and_centroid
from tse_analytics.modules.phenomaster.actimot.views.actimot_frames_widget_ui import Ui_ActimotFramesWidget


class ActimotFramesWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ActimotFramesWidget()
        self.ui.setupUi(self)

        self.ui.horizontalSlider.valueChanged.connect(self._slider_value_changed)

        self.df: pd.DataFrame | None = None
        self.frame_number: int = 0

    def set_data(self, df: pd.DataFrame) -> None:
        self.df = df
        self.ui.horizontalSlider.setMaximum(df.shape[0] - 1)
        self._update_plot()

    def resizeEvent(self, e):
        self._update_plot()

    def _slider_value_changed(self, value: int):
        self.frame_number = value
        self._update_plot()

    def _update_plot(self):
        if self.df is None:
            return

        if "X" not in self.df.columns:
            return

        row = self.df.iloc[self.frame_number]
        x_num = int(row.at["X"])
        y_num = int(row.at["Y"])

        pixmap, centroid = get_pixmap_and_centroid(x_num, y_num)
        pixmap = pixmap.scaled(self.ui.labelFrameImage.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.labelFrameImage.setPixmap(pixmap)
        self.ui.labelFrameNumber.setText(f"Frame: {self.frame_number}")
        self.ui.labelCentroid.setText(f"Centroid: [{centroid[1]}, {centroid[0]}]")
