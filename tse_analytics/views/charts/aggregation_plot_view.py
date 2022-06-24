from typing import Optional

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout
from tse_datatools.analysis.processor import apply_time_binning
from tse_datatools.data.animal import Animal
from tse_datatools.data.dataset_component import DatasetComponent

from tse_analytics.messaging.messages import BinningAppliedMessage


class AggregationPlotView(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.canvas = FigureCanvas(Figure(figsize=(5.0, 4.0), dpi=100))
        self.ax = self.canvas.figure.subplots()
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        self._data: Optional[DatasetComponent] = None
        self._animal_ids: Optional[list[int]] = None
        self._variable: Optional[str] = None

    def apply_binning(self, message: BinningAppliedMessage):
        df = self._data.df
        df = df[df['AnimalNo'].isin(self._animal_ids)]
        df = df.set_index('DateTime', drop=False)

        result = apply_time_binning(df, message.delta, message.unit, message.mode)

        self.ax.clear()
        result.set_index("Order", inplace=True)
        result.plot(y=self._variable, kind='bar', ax=self.ax)
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def set_data(self, data: DatasetComponent):
        self._data = data

    def set_animal_data(self, animals: list[Animal]):
        self._animal_ids = [animal.id for animal in animals]

    def set_variable(self, variable: str):
        self._variable = variable

    def clear(self):
        self.ax.clear()
        self._data = None
        self._animal_ids = None
        self._variable = None
