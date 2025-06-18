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
        """
        Initialize the PandasTableView widget.

        Args:
            parent: The parent widget. Default is None.
        """
        super().__init__(parent)
        self.verticalHeader().setDefaultSectionSize(20)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

    def set_data(self, df: pd.DataFrame):
        """
        Set the pandas DataFrame to be displayed in the table view.

        This method creates a new PandasSimpleModel with the provided DataFrame,
        sets it as the model for this view, and adjusts column widths to fit the content.

        Args:
            df: The pandas DataFrame to display.
        """
        model = PandasSimpleModel(df)
        self.setModel(model)
        self.resizeColumnsToContents()
