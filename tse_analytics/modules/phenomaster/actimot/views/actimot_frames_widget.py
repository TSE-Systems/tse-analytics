import numpy as np
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget

from tse_analytics.modules.phenomaster.actimot.views.actimot_frames_widget_ui import Ui_ActimotFramesWidget


class ActimotFramesWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.ui = Ui_ActimotFramesWidget()
        self.ui.setupUi(self)

        self.ui.horizontalSlider.valueChanged.connect(self.__slider_value_changed)

        self.df: pd.DataFrame | None = None
        self.frame_number: int = 0

    def set_data(self, df: pd.DataFrame) -> None:
        self.df = df
        self.ui.horizontalSlider.setMaximum(df.shape[0] - 1)
        self.__update_plot()

    def resizeEvent(self, e):
        self.__update_plot()

    def __slider_value_changed(self, value: int):
        self.frame_number = value
        self.__update_plot()

    def __update_plot(self):
        if self.df is None:
            return

        x_range = range(64)
        y_range = range(32)

        x1_column_index = self.df.columns.get_loc("X1") + 1  # +1 due to index column

        row = self.df.iloc[[self.frame_number]]

        datetime = row.iat[0, 0]
        bitmask = np.zeros([32, 64], dtype=np.uint8)

        for index_x in x_range:
            x = row.iat[0, x1_column_index + index_x - 1]
            for index_y in y_range:
                y = row.iat[0, x1_column_index + 64 + index_y - 1]
                bitmask[index_y, index_x] = 255 if (x == 0 and y == 0) else 0

        centroid = [np.average(indices) for indices in np.where(bitmask > 0)]

        image = QImage(bitmask, 64, 32, 64, QImage.Format.Format_Indexed8)
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.ui.labelFrameImage.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.labelFrameImage.setPixmap(pixmap)

        self.ui.labelFrameNumber.setText(f"Frame: {self.frame_number}")
        self.ui.labelDateTime.setText(f"DateTime: {datetime.isoformat(sep=" ", timespec="milliseconds")}")
        self.ui.labelCentroid.setText(f"Centroid: {centroid}")
