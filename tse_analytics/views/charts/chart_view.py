from typing import Optional

from PySide6.QtCharts import QChartView, QLineSeries, QChart, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QPointF, QDateTime, QDate, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget
from tse_datatools.data.animal import Animal
from tse_datatools.data.dataset import Dataset


class ChartView(QChartView):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing)
        self.chart().setTitle("Chart View")

        self.axis_x = None
        self.axis_y = None

        self._data: Optional[Dataset] = None
        self._animals: Optional[list[Animal]] = None
        self._variable: Optional[str] = None

    def set_data(self, data: Dataset):
        self._data = data

    def set_animal_data(self, animals: list[Animal]):
        self._animals = animals
        self.__update_plot()

    def set_variable(self, variable: str):
        self._variable = variable
        self.__update_plot()

    def __update_plot(self):
        if self._data is None or self._variable is None or self._animals is None or self._variable not in self._data.df:
            return

        self.chart().removeAllSeries()
        self.clear_axes()

        self.axis_x = QDateTimeAxis()
        self.axis_x.setTitleText("DateTime")

        self.axis_y = QValueAxis()
        self.axis_y.setTitleText(self._variable)

        x_min = None
        x_max = None
        y_min = None
        y_max = None
        for animal in self._animals:
            filtered_data = self._data.df[self._data.df['AnimalNo'] == animal.id]

            series = QLineSeries()
            series.setName(f'Animal {animal.id}')

            for index, row in filtered_data.iterrows():
                # date_time = QDateTime.fromString(row["DateTime"], "yyyy-MM-dd hh:mm:ss.zzz")
                date_time = QDateTime.fromMSecsSinceEpoch(int(row["DateTime"].value / 1000000))
                x = float(date_time.toMSecsSinceEpoch())
                y = float(row[self._variable])

                if x_min is None:
                    x_min = date_time
                    x_max = date_time
                    y_min = y
                    y_max = y
                else:
                    if date_time < x_min:
                        x_min = date_time
                    if date_time > x_max:
                        x_max = date_time
                    if y < y_min:
                        y_min = y
                    if y > y_max:
                        y_max = y

                series.append(x, y)
                series.attachAxis(self.axis_x)
                series.attachAxis(self.axis_y)

            self.axis_x.setRange(x_min, x_max)
            self.axis_y.setRange(y_min, y_max)

            self.chart().addSeries(series)

            self.chart().addAxis(self.axis_x, Qt.AlignBottom)
            self.chart().addAxis(self.axis_y, Qt.AlignLeft)

    def clear_axes(self):
        if self.axis_x is not None:
            self.chart().removeAxis(self.axis_x)
        if self.axis_y is not None:
            self.chart().removeAxis(self.axis_y)

    def clear(self):
        self.chart().removeAllSeries()
        self.clear_axes()
        self._data = None
        self._animals = None
