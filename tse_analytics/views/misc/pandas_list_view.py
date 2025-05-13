import pandas as pd
from PySide6.QtWidgets import QAbstractItemView, QListView, QWidget

from tse_analytics.core.models.pandas_list_model import PandasListModel


class PandasListView(QListView):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def set_data(self, df: pd.DataFrame):
        model = PandasListModel(df)
        self.setModel(model)
