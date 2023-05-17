from typing import Optional

import pandas as pd
from PySide6.QtWidgets import QWidget, QTableView

from tse_analytics.models.pandas_model import PandasModel


class CaloDetailsTableView(QTableView):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.verticalHeader().setDefaultSectionSize(20)

    def set_data(self, df: pd.DataFrame):
        model = PandasModel(df)
        self.setModel(model)
