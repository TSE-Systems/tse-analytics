import pandas as pd
from PySide6.QtWidgets import QTableView, QWidget

from tse_analytics.core.models.pandas_model import PandasModel


class CaloDetailsTableView(QTableView):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.verticalHeader().setDefaultSectionSize(20)

    def set_data(self, df: pd.DataFrame):
        model = PandasModel(df)
        self.setModel(model)
        self.setColumnWidth(0, 120)
