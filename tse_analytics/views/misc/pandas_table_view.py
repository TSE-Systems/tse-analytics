import pandas as pd
from PySide6.QtWidgets import QAbstractItemView, QTableView, QWidget

from tse_analytics.core.models.pandas_simple_model import PandasSimpleModel


class PandasTableView(QTableView):
    """
    A table view widget for displaying pandas DataFrame data.

    This widget provides a simple way to display pandas DataFrame data
    in a table format, with rows and columns matching the DataFrame structure.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.verticalHeader().setDefaultSectionSize(20)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def set_data(self, df: pd.DataFrame, resize_columns = True):
        model = PandasSimpleModel(df)
        self.setModel(model)
        if resize_columns:
            self.resizeColumnsToContents()
