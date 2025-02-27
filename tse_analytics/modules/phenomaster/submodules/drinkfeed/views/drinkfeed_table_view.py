import pandas as pd
from PySide6.QtWidgets import QTableView, QWidget

from tse_analytics.core.models.pandas_simple_model import PandasSimpleModel


class DrinkFeedTableView(QTableView):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.verticalHeader().setDefaultSectionSize(20)

    def set_data(self, df: pd.DataFrame):
        model = PandasSimpleModel(df)
        self.setModel(model)
